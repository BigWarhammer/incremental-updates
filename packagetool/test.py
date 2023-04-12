import shutil


def main():
    shutil.copy("../tmp_src/ui/close_layer.csb", "../tmp/ui/close_layer.csb")


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-importtimefromyaspin
#   import yaspinspinner=yaspin()spinner.start()time.sleep(3)# time consuming tasksspinner.stop()