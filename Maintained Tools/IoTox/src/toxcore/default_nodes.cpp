#include "iotox/toxcore/default_nodes.hpp"

#include <stdexcept>
#include <string>
#include <utility>

namespace iotox::toxcore {
namespace {

BootstrapEndpoint checked_endpoint(std::string_view text) {
    auto parsed = parse_bootstrap_endpoint(text);
    if (!parsed) {
        throw std::logic_error("invalid compiled IoTox default Tox node: " + parsed.status().message());
    }
    return std::move(parsed).value();
}

const std::vector<DefaultNodeRecord> &catalog_storage() {
    static const std::vector<DefaultNodeRecord> catalog{
        {DefaultNodeRole::bootstrap,
         checked_endpoint("144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C"),
         "Canada"},
        {DefaultNodeRole::bootstrap,
         checked_endpoint("205.185.115.131:53:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68"),
         "United States"},
        {DefaultNodeRole::bootstrap,
         checked_endpoint("tox1.mf-net.eu:33445:B3E5FA80DC8EBD1149AD2AB35ED8B85BD546DEDE261CA593234C619249419506"),
         "Germany"},
        {DefaultNodeRole::bootstrap,
         checked_endpoint("3.0.24.15:33445:E20ABCF38CDBFFD7D04B29C956B33F7B27A3BB7AF0618101617B036E4AEA402D"),
         "Singapore"},
        {DefaultNodeRole::bootstrap,
         checked_endpoint("tox.initramfs.io:33445:3F0A45A268367C1BEA652F258C85F4A66DA76BCAA667A49E770BCC4917AB6A25"),
         "Taiwan"},
        {DefaultNodeRole::bootstrap,
         checked_endpoint("tox.hidemybits.com:443:5D57B95EE4A7F37BA031DAD0CBD9510A9C96FFE09C1CE24A9C33746F39817D6E"),
         "United States"},
        {DefaultNodeRole::tcp_relay,
         checked_endpoint("205.185.115.131:443:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68"),
         "United States"},
        {DefaultNodeRole::tcp_relay,
         checked_endpoint("139.162.110.188:443:F76A11284547163889DDC89A7738CF271797BF5E5E220643E97AD3C7E7903D55"),
         "Canada"},
        {DefaultNodeRole::tcp_relay,
         checked_endpoint("172.104.215.182:443:DA2BD927E01CD05EBCC2574EBE5BEBB10FF59AE0B2105A7D1E2B40E49BB20239"),
         "United States"},
        {DefaultNodeRole::tcp_relay,
         checked_endpoint("144.172.88.203:443:2016A0F2797EE3A8B004BA623F11AAFC8146F1B8F45107232A1A1AECCE856674"),
         "United Arab Emirates"},
    };
    return catalog;
}

}  // namespace

std::span<const DefaultNodeRecord> default_node_catalog() {
    return catalog_storage();
}

std::vector<BootstrapEndpoint> default_bootstrap_nodes() {
    std::vector<BootstrapEndpoint> output;
    for (const DefaultNodeRecord &record : catalog_storage()) {
        if (record.role == DefaultNodeRole::bootstrap) {
            output.push_back(record.endpoint);
        }
    }
    return output;
}

std::vector<BootstrapEndpoint> default_tcp_relays() {
    std::vector<BootstrapEndpoint> output;
    for (const DefaultNodeRecord &record : catalog_storage()) {
        if (record.role == DefaultNodeRole::tcp_relay) {
            output.push_back(record.endpoint);
        }
    }
    return output;
}

std::string_view to_string(DefaultNodeRole role) {
    switch (role) {
        case DefaultNodeRole::bootstrap:
            return "bootstrap";
        case DefaultNodeRole::tcp_relay:
            return "tcp-relay";
    }
    return "unknown";
}

}  // namespace iotox::toxcore
