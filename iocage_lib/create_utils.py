import os
import subprocess

import iocage_lib.ioc_fstab


def strip_jail_for_base_jail(config: dict, release: str, iocroot: str, jail_uuid: str) -> dict:
    basedirs = [
        'bin', 'boot', 'lib', 'libexec', 'rescue', 'sbin', 'usr/bin', 'usr/include', 'usr/lib',
        'usr/libexec', 'usr/sbin', 'usr/share', 'usr/libdata', 'usr/lib32'
    ]

    if '-STABLE' in release:
        # HardenedBSD does not have this.
        basedirs.remove('usr/lib32')

    for base_dir in basedirs:
        source = os.path.join(
            iocroot, 'templates' if all(k not in release for k in ('-RELEASE', '-STABLE')) else 'releases',
            release, 'root', base_dir
        )
        destination = os.path.join(iocroot, 'jails', jail_uuid, 'root', base_dir)

        # This reduces the REFER of the basejail.
        # Just much faster by almost a factor of 2 than the builtins.
        subprocess.Popen(['rm', '-r', '-f', destination]).communicate()
        os.mkdir(destination)

        iocage_lib.ioc_fstab.IOCFstab(jail_uuid, 'add', source, destination, 'nullfs', 'ro', '0', '0', silent=True)
        config['basejail'] = 1

    return config
