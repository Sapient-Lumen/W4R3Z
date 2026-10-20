use std::time::Duration;

use anonssh::{
    tor_transport::{tor_v3_service_id_from_control_private_key, TorControlEndpoint},
    I2pDestinationBinding, I2pSamDialProvider, I2pSamListenProvider, TorOnionBinding,
    TorOnionListenProvider, TorSocksDialProvider,
};
use anonssh_bond::{EndpointProvider, FailureDomain, LaneConfig, LaneId, TrafficClass};
use anonssh_bond_tokio::{
    BondDialer, BondListener, BondProviderConfig, BondRuntimeConfig, BondSession, BondSessionKey,
    DialProviderSet, LaneDialProvider, LaneListenProvider, ListenProviderSet, ProviderLane,
    ProviderPolicy,
};
use data_encoding::BASE64;
use tokio::io::{AsyncBufReadExt, AsyncReadExt, AsyncWriteExt, BufReader};
use tokio::net::{TcpListener, TcpStream};
use zeroize::Zeroizing;

const TEST_TIMEOUT: Duration = Duration::from_secs(10);

#[tokio::test]
async fn public_tor_providers_dial_and_publish_exact_endpoints() {
    tokio::time::timeout(TEST_TIMEOUT, tor_provider_lifecycle())
        .await
        .expect("Tor provider lifecycle timed out");
}

async fn tor_provider_lifecycle() {
    let expanded_key = Zeroizing::new(BASE64.encode(&[0x42; 64]));
    let service_id = tor_v3_service_id_from_control_private_key(&expanded_key).unwrap();
    let endpoint = format!("tor://{service_id}.onion:2222");

    let socks = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let socks_addr = socks.local_addr().unwrap();
    let expected_host = format!("{service_id}.onion");
    let socks_task = tokio::spawn(async move {
        let (mut stream, _) = socks.accept().await.unwrap();
        let mut greeting = [0_u8; 2];
        stream.read_exact(&mut greeting).await.unwrap();
        assert_eq!(greeting[0], 5);
        let mut methods = vec![0_u8; usize::from(greeting[1])];
        stream.read_exact(&mut methods).await.unwrap();
        assert!(methods.contains(&0));
        stream.write_all(&[5, 0]).await.unwrap();

        let mut request = [0_u8; 4];
        stream.read_exact(&mut request).await.unwrap();
        assert_eq!(request, [5, 1, 0, 3]);
        let host_len = stream.read_u8().await.unwrap() as usize;
        let mut host = vec![0_u8; host_len];
        stream.read_exact(&mut host).await.unwrap();
        assert_eq!(String::from_utf8(host).unwrap(), expected_host);
        assert_eq!(stream.read_u16().await.unwrap(), 2222);
        stream
            .write_all(&[5, 0, 0, 1, 127, 0, 0, 1, 0, 80])
            .await
            .unwrap();
        stream.write_all(b"tor-dial-ok").await.unwrap();
    });

    let dial = TorSocksDialProvider::new(socks_addr.to_string(), 2222).unwrap();
    let mut stream = dial.dial(&endpoint).await.unwrap();
    let mut payload = [0_u8; 11];
    stream.read_exact(&mut payload).await.unwrap();
    assert_eq!(&payload, b"tor-dial-ok");
    socks_task.await.unwrap();

    let control = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let control_addr = control.local_addr().unwrap();
    let cookie = Zeroizing::new("ab".repeat(32));
    let control_service_id = service_id.clone();
    let control_task = tokio::spawn(async move {
        let (stream, _) = control.accept().await.unwrap();
        let mut reader = BufReader::new(stream);
        let mut line = String::new();
        reader.read_line(&mut line).await.unwrap();
        assert!(line.starts_with("AUTHENTICATE "));
        reader.get_mut().write_all(b"250 OK\r\n").await.unwrap();

        line.clear();
        reader.read_line(&mut line).await.unwrap();
        assert!(line.starts_with("ADD_ONION ED25519-V3:"));
        let target: std::net::SocketAddr = line
            .split_ascii_whitespace()
            .find_map(|field| field.strip_prefix("Port=2222,"))
            .unwrap()
            .parse()
            .unwrap();
        reader
            .get_mut()
            .write_all(format!("250-ServiceID={control_service_id}\r\n250 OK\r\n").as_bytes())
            .await
            .unwrap();
        let mut inbound = TcpStream::connect(target).await.unwrap();
        inbound.write_all(b"tor-listen-ok").await.unwrap();
    });

    let binding = TorOnionBinding::new(endpoint.clone(), 2222, expanded_key).unwrap();
    let listen = TorOnionListenProvider::new(
        TorControlEndpoint::from_cookie(control_addr.to_string(), cookie).unwrap(),
        [binding],
    )
    .unwrap();
    assert!(listen.bind("tor://denied.onion").await.is_err());
    let mut acceptor = listen.bind(&endpoint).await.unwrap();
    assert_eq!(acceptor.local_endpoint(), endpoint);
    let mut inbound = acceptor.accept().await.unwrap();
    let mut payload = [0_u8; 13];
    inbound.read_exact(&mut payload).await.unwrap();
    assert_eq!(&payload, b"tor-listen-ok");
    control_task.await.unwrap();
}

#[tokio::test]
async fn public_i2p_providers_dial_and_publish_exact_endpoints() {
    tokio::time::timeout(TEST_TIMEOUT, i2p_provider_lifecycle())
        .await
        .expect("I2P provider lifecycle timed out");
}

async fn i2p_provider_lifecycle() {
    let dial_sam = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let dial_sam_addr = dial_sam.local_addr().unwrap();
    let dial_task = tokio::spawn(async move {
        let (control, _) = dial_sam.accept().await.unwrap();
        let mut control = BufReader::new(control);
        sam_hello(&mut control).await;
        assert_eq!(read_line(&mut control).await, "DEST GENERATE\n");
        control
            .get_mut()
            .write_all(b"DEST REPLY PUB=client-public PRIV=client-private\n")
            .await
            .unwrap();
        let create = read_line(&mut control).await;
        assert!(create.starts_with("SESSION CREATE "));
        control
            .get_mut()
            .write_all(b"SESSION STATUS RESULT=OK DESTINATION=client-private\n")
            .await
            .unwrap();

        let (data, _) = dial_sam.accept().await.unwrap();
        let mut data = BufReader::new(data);
        sam_hello(&mut data).await;
        let connect = read_line(&mut data).await;
        assert!(connect.contains("DESTINATION=server-public"));
        let mut initial_payload = [0_u8; 11];
        data.read_exact(&mut initial_payload).await.unwrap();
        assert_eq!(&initial_payload, b"i2p-initial");
        data.get_mut()
            .write_all(b"STREAM STATUS RESULT=OK\n")
            .await
            .unwrap();
        data.get_mut().write_all(b"i2p-dial-ok").await.unwrap();
    });

    let dial = I2pSamDialProvider::new(dial_sam_addr.to_string(), None, 0).unwrap();
    let mut stream = dial
        .dial_with_initial_payload("i2p://server-public", b"i2p-initial")
        .await
        .unwrap();
    let mut payload = [0_u8; 11];
    stream.read_exact(&mut payload).await.unwrap();
    assert_eq!(&payload, b"i2p-dial-ok");
    dial_task.await.unwrap();

    let listen_sam = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let listen_sam_addr = listen_sam.local_addr().unwrap();
    let listen_task = tokio::spawn(async move {
        let (control, _) = listen_sam.accept().await.unwrap();
        let mut control = BufReader::new(control);
        sam_hello(&mut control).await;
        let create = read_line(&mut control).await;
        assert!(create.contains("ID=server_lane"));
        assert!(create.contains("DESTINATION=server-private"));
        control
            .get_mut()
            .write_all(b"SESSION STATUS RESULT=OK DESTINATION=server-private\n")
            .await
            .unwrap();

        let (accept, _) = listen_sam.accept().await.unwrap();
        let mut accept = BufReader::new(accept);
        sam_hello(&mut accept).await;
        let command = read_line(&mut accept).await;
        assert!(command.contains("STREAM ACCEPT ID=server_lane"));
        accept
            .get_mut()
            .write_all(b"STREAM STATUS RESULT=OK\npeer-public\ni2p-listen-ok")
            .await
            .unwrap();
    });

    let endpoint = "i2p://server-public";
    let binding = I2pDestinationBinding::new(
        endpoint,
        "server_lane",
        Zeroizing::new("server-private".to_owned()),
    )
    .unwrap();
    let listen = I2pSamListenProvider::new(listen_sam_addr.to_string(), [binding]).unwrap();
    assert!(listen.bind("i2p://denied").await.is_err());
    let mut acceptor = listen.bind(endpoint).await.unwrap();
    assert_eq!(acceptor.local_endpoint(), endpoint);
    let mut inbound = acceptor.accept().await.unwrap();
    let mut payload = [0_u8; 13];
    inbound.read_exact(&mut payload).await.unwrap();
    assert_eq!(&payload, b"i2p-listen-ok");
    listen_task.await.unwrap();
}

#[tokio::test]
async fn public_i2p_providers_form_an_authenticated_bond() {
    tokio::time::timeout(TEST_TIMEOUT, i2p_bond_lifecycle())
        .await
        .expect("I2P bonded provider lifecycle timed out");
}

async fn i2p_bond_lifecycle() {
    let listen_sam = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let listen_sam_addr = listen_sam.local_addr().unwrap();
    let dial_sam = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let dial_sam_addr = dial_sam.local_addr().unwrap();
    let router_task = tokio::spawn(async move {
        let (listener_control, _) = listen_sam.accept().await.unwrap();
        let mut listener_control = BufReader::new(listener_control);
        sam_hello(&mut listener_control).await;
        let create = read_line(&mut listener_control).await;
        assert!(create.contains("ID=bond_server"));
        assert!(create.contains("DESTINATION=server-private"));
        listener_control
            .get_mut()
            .write_all(b"SESSION STATUS RESULT=OK DESTINATION=server-private\n")
            .await
            .unwrap();

        let (dial_control, _) = dial_sam.accept().await.unwrap();
        let mut dial_control = BufReader::new(dial_control);
        sam_hello(&mut dial_control).await;
        assert_eq!(read_line(&mut dial_control).await, "DEST GENERATE\n");
        dial_control
            .get_mut()
            .write_all(b"DEST REPLY PUB=client-public PRIV=client-private\n")
            .await
            .unwrap();
        let create = read_line(&mut dial_control).await;
        assert!(create.starts_with("SESSION CREATE "));
        assert!(create.contains("DESTINATION=client-private"));
        dial_control
            .get_mut()
            .write_all(b"SESSION STATUS RESULT=OK DESTINATION=client-private\n")
            .await
            .unwrap();

        let (listener_result, dial_result) = tokio::join!(listen_sam.accept(), dial_sam.accept());
        let (listener_data, _) = listener_result.unwrap();
        let (dial_data, _) = dial_result.unwrap();
        let mut listener_data = BufReader::new(listener_data);
        sam_hello(&mut listener_data).await;
        assert!(read_line(&mut listener_data)
            .await
            .contains("STREAM ACCEPT ID=bond_server"));
        listener_data
            .get_mut()
            .write_all(b"STREAM STATUS RESULT=OK\n")
            .await
            .unwrap();

        let mut dial_data = BufReader::new(dial_data);
        sam_hello(&mut dial_data).await;
        assert!(read_line(&mut dial_data)
            .await
            .contains("DESTINATION=server-public"));

        // SAM must receive authenticated early data before it exposes the inbound stream.
        let mut magic = [0_u8; 4];
        dial_data.read_exact(&mut magic).await.unwrap();
        assert_eq!(&magic, b"ABJ1");
        dial_data
            .get_mut()
            .write_all(b"STREAM STATUS RESULT=OK\n")
            .await
            .unwrap();
        listener_data
            .get_mut()
            .write_all(b"client-public\n")
            .await
            .unwrap();
        listener_data.get_mut().write_all(&magic).await.unwrap();
        listener_data.get_mut().flush().await.unwrap();

        tokio::io::copy_bidirectional(&mut dial_data, &mut listener_data)
            .await
            .unwrap();
    });

    let lane = ProviderLane::new(
        LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(11).unwrap(),
            Duration::from_millis(20),
            10_000_000,
        )
        .unwrap(),
        EndpointProvider::I2p,
        "i2p://server-public",
    )
    .unwrap();
    let policy = ProviderPolicy::exact(1, 1, [lane.clone()], []).unwrap();
    let binding = I2pDestinationBinding::new(
        lane.endpoint(),
        "bond_server",
        Zeroizing::new("server-private".to_owned()),
    )
    .unwrap();
    let mut listen_providers = ListenProviderSet::new();
    listen_providers
        .register(I2pSamListenProvider::new(listen_sam_addr.to_string(), [binding]).unwrap())
        .unwrap();
    let listener = BondListener::bind(
        BondSessionKey::new([0x49; 32]),
        bond_provider_config(),
        policy.clone(),
        listen_providers,
        std::slice::from_ref(&lane),
    )
    .await
    .unwrap();

    let mut dial_providers = DialProviderSet::new();
    dial_providers
        .register(I2pSamDialProvider::new(dial_sam_addr.to_string(), None, 0).unwrap())
        .unwrap();
    let dialer = BondDialer::new(
        BondSessionKey::new([0x49; 32]),
        bond_provider_config(),
        policy,
        dial_providers,
    )
    .unwrap();

    let (client, server) = tokio::join!(
        dialer.connect(std::slice::from_ref(&lane)),
        listener.accept(std::slice::from_ref(&lane)),
    );
    let client = client.unwrap();
    let server = server.unwrap();
    assert_eq!(client.session_id(), server.session_id());
    assert_eq!(
        client.server_incarnation(),
        Some(listener.server_incarnation())
    );
    exchange_bond_payload(&client, &server).await;

    let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
    client_result.unwrap();
    server_result.unwrap();
    listener.shutdown().await;
    router_task.await.unwrap();
}

async fn exchange_bond_payload(client: &BondSession, server: &BondSession) {
    let payload = b"encrypted over a high-level I2P provider bond";
    let mut outbound = client.open_stream(TrafficClass::Interactive).await.unwrap();
    let mut inbound = server.accept_stream().await.unwrap();
    let mut received = vec![0_u8; payload.len()];
    let (sent, read) = tokio::join!(
        outbound.write_all(payload),
        inbound.read_exact(&mut received)
    );
    sent.unwrap();
    read.unwrap();
    assert_eq!(received, payload);

    let response = b"authenticated response";
    let mut echoed = vec![0_u8; response.len()];
    let (sent, read) = tokio::join!(
        inbound.write_all(response),
        outbound.read_exact(&mut echoed)
    );
    sent.unwrap();
    read.unwrap();
    assert_eq!(echoed, response);
    let (outbound_closed, inbound_closed) = tokio::join!(outbound.shutdown(), inbound.shutdown());
    outbound_closed.unwrap();
    inbound_closed.unwrap();
}

fn bond_provider_config() -> BondProviderConfig {
    BondProviderConfig::new(
        BondRuntimeConfig::default(),
        Duration::from_secs(2),
        Duration::from_secs(2),
    )
    .unwrap()
}

async fn sam_hello(reader: &mut BufReader<TcpStream>) {
    assert_eq!(read_line(reader).await, "HELLO VERSION MIN=3.0 MAX=3.3\n");
    reader
        .get_mut()
        .write_all(b"HELLO REPLY RESULT=OK VERSION=3.3\n")
        .await
        .unwrap();
}

async fn read_line(reader: &mut BufReader<TcpStream>) -> String {
    let mut line = String::new();
    reader.read_line(&mut line).await.unwrap();
    line
}
