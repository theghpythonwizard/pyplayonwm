from pyplayonwm import _install_handbrake


def hb_installer():
    runner = _install_handbrake.HandBrakeInstaller()
    if runner.handbrake_installed():
        pass
    else:
        runner.install_handbrake()
    

if __name__ == '__main__':
    hb_installer()