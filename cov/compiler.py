# coding=utf-8
import os
import commands
import conf

class Compiler:
    def __init__(self, name, repos_type, repos_addr):
        self._name = name
        self._repos_type = repos_type
        self._repos_addr = repos_addr

    def init_work_space(self, work_space):
        self._work_space = work_space

        self._code_dir = os.path.join(self._work_space, "code")
        self._out_dir = os.path.join(self._work_space, "out")
        self._upload_dir = os.path.join(self._work_space, "upload")
        self._report_dir = os.path.join(self._work_space, "report")

        os.system("rm -rf %s" % self._work_space)
        os.system("mkdir -p %s %s %s %s %s" %(self._work_space,
                                              self._code_dir,
                                              self._out_dir,
                                              self._upload_dir,
                                              self._report_dir))

    def check_repos(self):
        ret = os.system("which svn")
        if 0 != ret:
            print "[error] no svn installed."
            return 1

        if self._repos_type == "svn":
            ret = os.system("svn info %s" %self._repos_addr)
            if 0 != ret:
                print "[error] invalid svn addr: %s" %self._repos_addr
                return 1
        else:
            print "[error] unknow repos_type: %s" % self._repos_type
            return 1

        return 0

    def check_reversion(self, version):
        if self._repos_type == "svn":
            ret = os.system("svn info %s -r %s" % (self._repos_addr, version))
            if 0 != ret:
                print "[error] invalid svn addr: %s" %self._repos_addr
                return 1
        else:
            print "[error] unknow repos_type: %s" %self._repos_type
            return 1

        return 0

    def download_code(self, version=""):
        os.system("rm -rf %s" % self._code_dir)

        ret = self.check_repos()
        if 0 != ret:
            return 1

        if 0 < len(version):
            ret = self.check_reversion(version)
            if 0 != ret:
                return 1

        shell = "svn export %s" % self._repos_addr
        if "" != version:
            shell += " -r %s" %version

        shell += ' ' + self._code_dir

        ret = os.system(shell)
        if 0 != ret:
            print "error download_code failed! cmd=%s" %shell
            return 1

        return 0

    def modify_code_for_coverate(self):
        shell = "grep -n 'protected void onDestroy\(\)' %s/src/com/meilishuo/app/activity/MainActivity.java | awk -F':' '{print $1}'" %self._code_dir
        ret, line_begin = commands.getstatusoutput(shell)
        if 0 != ret:
            print "[error] modify_code_for_coverate get line_begin failed!\n        cmd=%s" %shell
            return 1

        shell = "sed -n '/onDestroy\(\)/,/}/p' %s/src/com/meilishuo/app/activity/MainActivity.java | wc -l" %self._code_dir
        ret, line_count = commands.getstatusoutput(shell)
        if 0 != ret:
            print "[error] modify_code_for_coverate get line_count failed.\n        cmd=%s" %shell
            return 1

        line_target = int(line_begin) + int(line_count) - 1

        if conf.ENV == u'mac':
            shell = "sed -i '' $'%di\\\n System.exit(1);\n' %s/src/com/meilishuo/app/activity/MainActivity.java" %(line_target, self._code_dir)
        else:
            shell = "sed -i $'%di System.exit(1);\n' %s/src/com/meilishuo/app/activity/MainActivity.java" %(line_target, self._code_dir)

        ret, _ = commands.getstatusoutput(shell)
        if 0 != ret:
            print "[error] modify_code_for_coverate insert code failed.\n        cmd=%s" %shell
            return 1

        return 0

    def init_env(self):
        ANDROID_BUILD_TOOLS = conf.ANDROID_BUILD_TOOLS

        ANDROID_HOME = ANDROID_BUILD_TOOLS + u'/android-sdk-macosx'
        ANDROID_HOME_TOOLS = ANDROID_HOME + u'/tools'
        ANDROID_HOME_PLAT_TOOLS = ANDROID_HOME + u'/platform-tools'
        ANDROID_HOME_BUILD_TOOLS = ANDROID_HOME + u'/build-tools'

        ANT_HOME = ANDROID_BUILD_TOOLS + u'/apache-ant-1.9.4'
        ANT_HOME_BIN = ANT_HOME + u'/bin'

        NBS_JAR = ANDROID_BUILD_TOOLS + u'/nbs.newlens.class.rewriter.jar'
        ASPECTJ_HOME = ANDROID_BUILD_TOOLS + u'/aspectj-1.8.6'

        os.environ['ANDROID_HOME'] = ANDROID_HOME
        os.environ['PATH'] = ANDROID_HOME_TOOLS\
                             + u':' + ANDROID_HOME_PLAT_TOOLS\
                             + u':' + ANDROID_HOME_BUILD_TOOLS\
                             + u':' + os.environ['PATH']
        os.environ['ANT_HOME'] = ANT_HOME
        os.environ['PATH'] = ANT_HOME_BIN\
                             + ':' + os.environ['PATH']

        os.environ["ANT_OPTS"] = "-javaagent:" + NBS_JAR
        os.environ["_JAVA_OPTIONS"] = "-Xms4048m -Xmx4048m -verbosegc"

        if conf.ENV == u'mac':
            os.system("sed -i '' 's|aspectj\.home=.*|aspectj\.home=%s|' %s/ant.properties" %(ASPECTJ_HOME, self._code_dir))
            os.system("sed -i '' 's|sdk\.dir=.*|sdk\.dir=%s|' %s/ant.properties" %(ANDROID_HOME, self._code_dir))
        else:
            os.system("sed -i 's|aspectj\.home=.*|aspectj\.home=%s|' %s/ant.properties" %(ASPECTJ_HOME, self._code_dir))
            os.system("sed -i 's|sdk\.dir=.*|sdk\.dir=%s|' %s/ant.properties" %(ANDROID_HOME, self._code_dir))

    def compile(self):
        self.modify_code_for_coverate()
        self.init_env()
        ret = os.system("cd %s && android update project --path . && ant clean instrument > compile.log 2&>1" % self._code_dir)
        #ret = os.system("cd %s && android update project --path . && ant clean debug" % self._code_dir)
        #ret = os.system("cd %s && android update project --path . && ant clean release" % self._code_dir)
        if 0 != ret:
            print "[error] compile failed!"
            return ret

        ret = os.system("mv %s/bin/WelcomeActivity-instrumented.apk %s" % (self._code_dir, self._out_dir))
        #ret = os.system("mv %s/bin/WelcomeActivity-debug.apk %s" % (self._code_dir, self._out_dir))
        #ret = os.system("mv %s/bin/WelcomeActivity-release.apk %s" % (self._code_dir, self._out_dir))

        ret = os.system("mv %s/bin/coverage.em %s" % (self._code_dir, self._out_dir))
        ret = os.system("mv %s/src %s" % (self._code_dir, self._out_dir))
        ret = os.system("mv %s/src %s" % (self._code_dir, "compile.log"))
        ret = os.system("rm -rf %s" % self._code_dir)

        return 0


if __name__ == '__main__':
    module = Compiler("meilishuo-android",
                    "svn",
                    "http://svn.meilishuo.com/repos/meilishuo/mobile/Android/branches/6.7.0/Meilishuo")
    module.init_work_space("/Users/MLS/temp/task_0")
    module.download_code("")
    module.compile()