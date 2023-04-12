import json
import os
import time
from hashlib import md5

domain_name = "dev-download.k7.cn"
first_dir = "app-update"
searchPaths = ''
exclude_files = ['version.manifest', 'project.manifest', 'README.md']
exclude_dirs = ['.git', '.svn']


def save_version_manifest(res_key, version, resVersion):
    version_manifest = {"packageUrl": "http://{}/{}/{}/".format(domain_name, first_dir, res_key),
                        "remoteManifestUrl": "http://{}/{}/{}/v{}/project.manifest".format(domain_name, first_dir,
                                                                                           res_key, resVersion),
                        "remoteVersionUrl": "http://{}/{}/{}/version.manifest".format(domain_name, first_dir, res_key),
                        "version": version,
                        "resVersion": resVersion,
                        "engineVersion": "1.0.0.0"}
    return json.dumps(version_manifest, ensure_ascii=False, indent=2)


def save_project_manifest(folder, res_key, version, resVersion):
    data = get_filedic(folder)
    project_manifest = {"packageUrl": "http://{}/{}/{}/v{}/".format(domain_name, first_dir, res_key, resVersion),
                        "remoteManifestUrl": "http://{}/app-res/{}/v{}/project.manifest".format(domain_name, res_key,
                                                                                                resVersion),
                        "remoteVersionUrl": "http://{}/{}/{}/version.manifest".format(domain_name, first_dir, res_key),
                        "version": version,
                        "resVersion": resVersion,
                        "engineVersion": "1.0.0.0",
                        "assets": data, "searchPaths": [searchPaths]}
    return json.dumps(project_manifest, ensure_ascii=False, indent=2)


def get_filedic(folder):
    filedic = {}
    for root, dirs, files in os.walk(folder):
        if is_exclude_dir(root):
            continue
        for filename in files:
            if filename in exclude_files:
                continue
            fpath = os.path.join(root, filename)
            fmd5 = md5_file(fpath)
            if filename[-3:] == 'zip':
                infodic = {'md5': fmd5, 'compressed': True}
            else:
                infodic = {'md5': fmd5}
            relpath = os.path.relpath(fpath, folder)
            if os.sep == '\\':
                relpath = relpath.replace('\\', '/')
            filedic.setdefault(relpath, infodic)
    return filedic


def is_exclude_dir(s):
    for d in exclude_dirs:
        if s.find('/{}'.format(d)) != -1 or s.find('\\{}'.format(d)) != -1:
            return True
    return False


def md5_file(name):
    m = md5()
    a_file = open(name, 'rb')  # 需要使用二进制格式读取文件内容
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()


def main():
    resKey = "guandan"
    resVersion = "0.0.2"
    buildNum = "2"
    # 上传version_manifest
    version = time.strftime('%y%m%d', time.localtime(time.time())) + '.' + buildNum
    version_manifest_data = save_version_manifest(res_key=resKey, version=version, resVersion=resVersion)
    version_manifest_key = first_dir + '/' + resKey + '/' + 'version.manifest'
    with open("../output/version.manifest", 'w') as f:
        f.write(version_manifest_data)

    # 上传project_manifest
    project_manifest_data = save_project_manifest(folder="../output", res_key=resKey, version=version, resVersion=resVersion)
    project_manifest_key = first_dir + '/' + resKey + '/v' + resVersion + '/' + 'project.manifest'
    with open("../output/project.manifest", 'w') as f:
        f.write(project_manifest_data)


if __name__ == "__main__":
    main()
