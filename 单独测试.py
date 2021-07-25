import random

from selenium import webdriver
import slideVerCode as SV #导入
import requests,time
from selenium.webdriver.common.action_chains import ActionChains
class crackAccount():
    def __init__(self,account,password,url):
        self.driver=webdriver.Chrome()
        self.account=account
        self.password=password
        self.url=url
        pass
    def crack(self):
        self.driver.get(self.url)
        time.sleep(2)
        self.driver.find_element_by_xpath("//*[@id=\"dologin\"]").click()
        time.sleep(1)
        self.driver.switch_to.frame("loginIframe")
        self.driver.find_element_by_xpath("//*[@id=\"switcher_plogin\"]").click()
        time.sleep(1)
        self.driver.find_element_by_xpath("//*[@id=\"u\"]").send_keys(self.account)
        self.driver.find_element_by_xpath("//*[@id=\"p\"]").send_keys(self.password)
        time.sleep(1)
        self.driver.find_element_by_xpath("//*[@id=\"login_button\"]").click()
        time.sleep(1)
        self.driver.switch_to.frame("tcaptcha_iframe")
        time.sleep(1)
        self.crackVerCode()



    def crackVerCode(self):
        #获得背景图片
        def getBgImg():
            bgUrl=self.driver.find_element_by_xpath("//*[@id=\"slideBg\"]").get_attribute("src")
            ir = requests.get(bgUrl)

            if ir.status_code == 200:
                with open("bg.jpg",'wb') as f:
                    f.write(ir.content)
            else:
                print("验证码背景下载失败")
            pass


        moveList=SV.run('bg.jpg')
        print(moveList)
        slide = self.driver.find_element_by_xpath("//*[@id=\"tcaptcha_drag_thumb\"]")
        action = ActionChains(self.driver)
        action.click_and_hold(slide)
        for i in moveList:
            action.move_by_offset(xoffset=i, yoffset=0).perform()
            #
        time.sleep(0.5)
        action.reset_actions()
        action.release().perform()

    def run(self):
        self.crack()
if __name__ == '__main__':

    aobj=crackAccount("账号","密码","https://cf.qq.com/cp/a20210619hero/index.shtml")
    aobj.run()
