{ pkgs
, ratoxTestHarnessAarch64
, iotoxRescueToolboxAarch64
, aarch64Kernel
, aarch64Busybox
}:

let
  closure = pkgs.closureInfo {
    rootPaths = [ ratoxTestHarnessAarch64 iotoxRescueToolboxAarch64 ];
  };
  init = pkgs.writeText "iotox-aarch64-rescue-init" ''
    #!/bin/busybox sh
    export PATH=/bin
    mkdir -p /proc /sys /dev /dev/pts /tmp /home/operator
    mount -t proc proc /proc
    mount -t sysfs sysfs /sys
    mount -t devtmpfs devtmpfs /dev
    mkdir -p /dev/pts
    mount -t devpts devpts /dev/pts
    chmod 1777 /tmp
    chmod 0700 /home/operator
    chown 1000:1000 /home/operator
    printf 'root:x:0:0:root:/root:/bin/sh\noperator:x:1000:1000:operator:/home/operator:/bin/sh\n' > /etc/passwd
    printf 'root:x:0:\noperator:x:1000:\n' > /etc/group
    echo "aarch64-kernel=$(uname -m)"
    su -s /bin/sh operator -c \
      '${ratoxTestHarnessAarch64}/bin/iotox_terminal_posix_process_tests --rescue-toolbox-qualification ${ratoxTestHarnessAarch64}/bin/iotox ${iotoxRescueToolboxAarch64}/bin/oksh ${iotoxRescueToolboxAarch64}/bin'
    result=$?
    if [ "$result" -eq 0 ]; then
      echo IOTOX-AARCH64-KERNEL-RESCUE-PASS
    else
      echo "IOTOX-AARCH64-KERNEL-RESCUE-FAIL=$result"
    fi
    sync
    poweroff -f
  '';
  initramfs = pkgs.runCommand "iotox-aarch64-rescue-initramfs.cpio.gz" {
    nativeBuildInputs = [ pkgs.cpio pkgs.gzip ];
  } ''
    root="$PWD/root"
    mkdir -p "$root/bin" "$root/etc" "$root/nix/store"
    install -m 0755 ${aarch64Busybox}/bin/busybox "$root/bin/busybox"
    for command in sh mount mkdir chmod chown uname su sync poweroff; do
      ln -s busybox "$root/bin/$command"
    done
    install -m 0755 ${init} "$root/init"
    while IFS= read -r store_path; do
      mkdir -p "$root$(dirname "$store_path")"
      cp -a "$store_path" "$root$store_path"
    done < ${closure}/store-paths
    (cd "$root" && find . -print0 | cpio --null --create --format=newc --quiet) \
      | gzip -9 > "$out"
  '';
in
pkgs.runCommand "iotox-ratox-rescue-toolbox-aarch64-system" {
  nativeBuildInputs = [ pkgs.coreutils pkgs.gnugrep pkgs.qemu ];
} ''
  trap 'cat transcript >&2' ERR
  timeout 180 qemu-system-aarch64 \
    -machine virt -cpu cortex-a57 -accel tcg,thread=multi \
    -smp 2 -m 1024 -nographic -no-reboot \
    -kernel ${aarch64Kernel}/Image \
    -initrd ${initramfs} \
    -append 'console=ttyAMA0 rdinit=/init panic=-1' \
    > transcript 2>&1
  tr -d '\r' < transcript > normalized
  grep -Fxq 'aarch64-kernel=aarch64' normalized
  grep -Fq 'terminal rescue toolbox qualification passed' normalized
  grep -Fxq 'IOTOX-AARCH64-KERNEL-RESCUE-PASS' normalized
  cp transcript "$out"
''
