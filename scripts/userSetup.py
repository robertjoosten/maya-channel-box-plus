from maya import cmds


def main():
    from channel_box_plus import install
    install.execute()


if not cmds.about(batch=True):
    cmds.evalDeferred(main)
