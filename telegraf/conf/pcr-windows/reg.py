import winreg


def main():
    env_file = 'telegraf.env'
    f = open(env_file, 'r', encoding='utf-8')
    envs = []
    for l in f:
        if l:
            envs.append(l.strip())

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Services\telegraf', 0,
                         winreg.KEY_SET_VALUE)

    winreg.SetValueEx(key, 'Environment', 0, winreg.REG_MULTI_SZ, envs)

    if key:
        winreg.CloseKey(key)


if __name__ == "__main__":
    """
    将环境变量注册到服务中
    """
    main()
