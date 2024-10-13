import os
from pathlib import Path

import requests
from robocorp import browser
from robocorp.tasks import task
import requests
import pandas as pd
from RPA.PDF import PDF
from RPA.Archive import Archive
pdf = PDF()
folder = os.curdir+'/rpapdf'
browser.configure(
        slowmo=100,
        browser_engine='chrome',
        headless=False
    )
page= browser.goto("https://robotsparebinindustries.com/")
archive = Archive()
@task
def order_robots_from_RobotSpareBin():
    open_robot_order_website()
    path= os.curdir+"\order.csv"
    download_csv(path)
    create_order(path)
    archive.add_to_archive(folder,folder+'/orders.zip')

def open_robot_order_website():
    page.fill('//input[@id="username"]','maria')
    page.fill('//input[@id="password"]','thoushallnotpass')
    page.click("//button[text()='Log in']")
    page.click("//a[text()='Order your robot!']")
    page.wait_for_selector("//p[text()='By using this order form, I give up all my constitutional rights for the benefit of RobotSpareBin Industries Inc.']//following::div//button[text()='OK']")
    page.click("//p[text()='By using this order form, I give up all my constitutional rights for the benefit of RobotSpareBin Industries Inc.']//following::div//button[text()='OK']")
    return page
def download_csv(path):
    response = requests.get('https://robotsparebinindustries.com/orders.csv')
    if os.path.isfile(path):
        os.remove(path)
        print('file removed')
    with open(path, 'wb') as file:
        file.write(response.content)
    print('File downloaded successfully')

def create_order(path):   
       csvFile = pd.read_csv(path)
       for index, row in csvFile.iterrows():
           page.fill("//label[contains(text(),'Legs')]/following::input[@placeholder='Enter the part number for the legs']",str(row['Legs']))
           page.fill("//input[@id='address']",str(row['Legs']))
           page.check(f"//input[@id='id-body-{row['Body']}']")
           page.select_option(f"//select[@id='head']",value=str(row['Head']))
           page.click("//*[@id='order']")
           try:
               error = page.is_enabled("//div[@class='alert alert-danger' and @role='alert']",timeout=10000)
           except:
               error = False
           print(error)
           while error:
               page.click("//*[@id='order']")
               try:
                error = page.is_enabled("//div[@class='alert alert-danger' and @role='alert']",timeout=10000)
               except:
                error = False 
           page.wait_for_selector('//*[@id="receipt"]/h3')
           print('take screenshot')
           if os.path.isdir(folder):
            print('folder exists')
           else:
                os.mkdir(folder)
           page.screenshot(path=folder+'/'+f'{row["Order number"]}.png')
           print('screenshot saved')
           pdf.add_files_to_pdf(
            files=[folder+'/'+f'{row["Order number"]}.png'],
            target_document=folder+'/'+f'{row["Order number"]}.pdf'
            )
           os.remove(folder+'/'+f'{row["Order number"]}.png')
           page.click('//*[@id="order-another"]')
           page.click("//p[text()='By using this order form, I give up all my constitutional rights for the benefit of RobotSpareBin Industries Inc.']//following::div//button[text()='OK']")