# coding=utf-8
import io
import os
import sys

import yaml
import shutil
import zipfile
import pathlib
import datetime
import argparse
from yaspin import yaspin
from loguru import logger


def isdir(file):
    return file[-1] == "/"


class PackageTool:
    def __init__(self):
        self._op_path = None
        self._dest_path = None
        self._src_path = None
        self._tmp_path = None
        self.pkg_cfg = None
        self._miss_file_list = []
        self._unlink_file_list = []
        logger.add("./log/log_{time}.log")

    def set_package_path(self, src_path, dest_path):
        self._src_path = src_path
        self._dest_path = dest_path
        self._op_path = "tmp_src"
        self._tmp_path = "tmp"

    def load_package_rules(self, yaml_path):
        with open(yaml_path, 'r', encoding='UTF-8') as file:
            pkg_cfg = yaml.safe_load(file)
        self.pkg_cfg = pkg_cfg

    def start_package(self):
        """
        开始执行
        :return:
        """
        self.do_prepare()
        self.clear_unused(self.pkg_cfg["unused"])
        rules = self.pkg_cfg["rules"]
        self.execute_rules(rules)
        self.output_result()

    def do_prepare(self):
        spinner = yaspin(text="Loading", color="yellow")
        spinner.start()
        if os.path.exists(self._op_path):
            shutil.rmtree(self._op_path)
        if os.path.exists(self._dest_path):
            shutil.rmtree(self._dest_path)
        logger.info("do_prepare mkdir [{0}]".format(self._dest_path))
        os.mkdir(self._dest_path)
        shutil.copytree(self._src_path, self._op_path)
        spinner.stop()

    def parse_rule(self, rule_name):
        """
        解析规则
        :param rule_name:规则名
        :return: void
        """
        full_name = "rule-" + rule_name
        if full_name in self.pkg_cfg:
            self.prepare_tmp()
            logger.info("do rule [{0}]".format(rule_name))
            rule = self.pkg_cfg[full_name]
            if "sub_rules" in rule:
                sub_rules = rule["sub_rules"]
                for sub_rule in sub_rules:
                    if "rule-" + sub_rule in self.pkg_cfg:
                        self.execute_rule(self.pkg_cfg["rule-" + sub_rule])
            self.execute_rule(rule)
            self.package(rule_name)

    def clear_unused(self, unused_list):
        for unused_file in unused_list:
            full_path = os.path.join(self._op_path, unused_file)
            if os.path.exists(full_path):
                if isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)

    def execute_rules(self, rules):
        for rule in rules:
            self.parse_rule(rule)

    def execute_rule(self, rule):
        """
        执行规则
        :param rule: 规则
        :return: void
        """
        container = rule["container"]
        for item in container:
            file = os.path.join(self._op_path, item)
            if os.path.exists(file):
                self.copy_file(file, os.path.join(self._tmp_path, item))
            else:
                self.record_miss_file(item)

    def copy_file(self, file, dest_path):
        logger.debug("Copying file {0} {1}".format(file, dest_path))
        if isdir(file):
            shutil.copytree(file, dest_path, dirs_exist_ok=True)
            shutil.rmtree(file)
        else:
            parent_dir = pathlib.Path(dest_path).parent
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            shutil.copy2(file, dest_path)
            os.remove(file)

    def prepare_tmp(self):
        if os.path.exists(self._tmp_path):
            shutil.rmtree(self._tmp_path)
        os.mkdir(self._tmp_path)

    def package(self, rule_name):
        myzip = zipfile.ZipFile(os.path.join(self._dest_path, rule_name + ".zip"), "w", strict_timestamps=False)
        for root, dirs, files in os.walk(self._tmp_path):
            for name in files:
                file_name = os.path.join(root, name)
                zip_name = file_name[len(self._tmp_path):]
                myzip.write(file_name, zip_name, compress_type=zipfile.ZIP_DEFLATED)
        myzip.close()

    def record_miss_file(self, file):
        self._miss_file_list.append(file)

    def record_unlink_files(self):
        for root, dirs, files in os.walk(self._op_path):
            for name in files:
                file_name = os.path.join(root, name)
                unlink_name = file_name[len(self._op_path):]
                self._unlink_file_list.append(unlink_name)

    def output_result(self):
        self.record_unlink_files()
        filename = './log/result_%s.txt' % datetime.datetime.now().strftime("%Y-%m-%d")
        with open(filename, 'a') as file_object:
            file_object.write("--------------------------------\n")
            file_object.write("**********Missing Files*********\n")
            for file in self._miss_file_list:
                file_object.write(file + "\n")
            file_object.write("**********Unlinked Files*********\n")
            for file in self._unlink_file_list:
                file_object.write(file + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="目标路径", default="../res")
    parser.add_argument("-s", "--src", help="源路径", default="../output")
    parser.add_argument("-c", "--config", help="配置文件", default="../config/packcfg.yaml")
    args = parser.parse_args()
    package_tool = PackageTool()
    package_tool.set_package_path(os.path.join(os.getcwd(), args.src), os.path.join(os.getcwd(), args.dir))
    package_tool.load_package_rules(os.path.join(os.getcwd(), args.config))
    package_tool.start_package()


if __name__ == "__main__":
    main()
