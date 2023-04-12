from packagetool.PackageTool import PackageTool
import os
import zipfile

srcPath = os.path.join(os.getcwd(), "res")
destPath = os.path.join(os.getcwd(), "output")


packageTool = PackageTool()
packageTool.set_package_path(srcPath, destPath)
packageTool.load_package_rules(os.path.join(os.getcwd(), "config/packcfg.yaml"))
packageTool.start_package()

# def test():
#     myzip = zipfile.ZipFile("./output/test.zip", "w")
#     for root, dirs, files in os.walk("./tmp"):
#         for name in files:
#             file_name = os.path.join(root, name)
#             zip_name = file_name[5:]
#             print(zip_name)
#             myzip.write(file_name, zip_name, compress_type=zipfile.ZIP_DEFLATED)
#         for name in dirs:
#             print(os.path.join(root, name))
#     myzip.close()
#
#
# test()
