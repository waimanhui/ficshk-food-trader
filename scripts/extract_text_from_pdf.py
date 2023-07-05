from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import csv
from datetime import datetime

FIRSTPAGETOP_Y1=601.52
PAGETOP_Y1=673.57
FOOTER_Y1=31.65
REGNO_X0=151.00
ADDRESS_X0=247.00
TELNO_X0=458.00
ITEM_X0=534.00
IMPORTER_X0=ITEM_X0
DISTRIBUTOR_X0=588.00
FOODCLASS_X0=654.00
YESNO_WIDTH=15.507

PDFfilename = "../data/registerTrader.pdf"
CSVfilename = "../data/registerTrader.csv"

header = ["Business Name 業務名稱", "Registration No. 登記號碼 / Reference No. 參考號碼","Business Address 業務地址", "Tel. No. 電話號碼", "Main Food Category 主要食物類別", "Importer 進口商", "Distributor 分銷商","Food Classification 食物分類"]
data = []
# data = [
#     ["合威菓菜","TR-22-002006","Shops D & E, G/F, 8 Fat Tseung Street,Cheung Sha Wan, KL","96615023","Fruit and vegetables (other than snack food, juices and Chinese herbs)水果及蔬菜 (小食食品、果汁或蔬菜汁及中草藥除外)","Yes","Yes","Vegetable products, including mushrooms, fungi and seaweed products 蔬菜製品，包括菇、真菌及海藻製品"],
#     ["合威菓菜","TR-22-002006","Shops D & E, G/F, 8 Fat Tseung Street,Cheung Sha Wan, KL","96615023","Fruit and vegetables (other than snack food, juices and Chinese herbs)水果及蔬菜 (小食食品、果汁或蔬菜汁及中草藥除外)","Yes","Yes","Fruit products 水果製品"],
#     ["合威菓菜","TR-22-002006","Shops D & E, G/F, 8 Fat Tseung Street,Cheung Sha Wan, KL","96615023","Fruit and vegetables (other than snack food, juices and Chinese herbs)水果及蔬菜 (小食食品、果汁或蔬菜汁及中草藥除外)","Yes","Yes","Fruit 水果"],
#     ["合威菓菜","TR-22-002006","Shops D & E, G/F, 8 Fat Tseung Street,Cheung Sha Wan, KL","96615023","Fruit and vegetables (other than snack food, juices and Chinese herbs)水果及蔬菜 (小食食品、果汁或蔬菜汁及中草藥除外)","Yes","Yes","Vegetables, including mushrooms, fungi and seaweed 蔬菜，包括菇、真菌及海藻"],
#     ["土作坊","TR-22-001785","香港灣仔石水渠街85號","25962580","Beverages (other than milk and dairy products) 飲料(奶及乳製品除外)","Yes","Yes","Coffee beans, tea leaves, instant drink mixes 咖啡豆、茶葉、沖劑飲品"],
#     ["土作坊","TR-22-001785","香港灣仔石水渠街85號","25962580","Beverages (other than milk and dairy products) 飲料(奶及乳製品除外)","Yes","Yes","Other non-alcoholic beverages 其他不含酒精飲料"],
#     ["土作坊","TR-22-001785","香港灣仔石水渠街85號","25962580","Beverages (other than milk and dairy products) 飲料(奶及乳製品除外)","Yes","Yes","Fresh fruit and vegetable juice, fruit and vegetable juice drink 新鮮果汁及蔬菜汁、果汁及蔬菜汁飲品"],
#     ["土作坊","TR-22-001785","香港灣仔石水渠街85號","25962580","Cereal and grain products (other than bakery products and snack food) 穀類及穀物製品(烘焙食品及小食食品除外)","Yes","Yes","Cereals, rice, wheat 穀類、大米、小麥"],
#     ["土作坊","TR-22-001785","香港灣仔石水渠街85號","25962580","Cereal and grain products (other than bakery products and snack food) 穀類及穀物製品(烘焙食品及小食食品除外)","Yes","Yes","Flour, starch, substitute flour 麵粉、澱粉、麵粉代用品"],
# ]

n=0
filedate=""

distributor_list=[]
newdistributor=False
distributor_name=""
distributor_regNo=""
distributor_address=""
distributor_TelNo=""
distributor_y1=0
pagenumber=0

foodCategory_list=[]
foodCategory={}
distributor={}

for page_layout in extract_pages(PDFfilename):
    # initialize page variables
    item_importer_list=[]
    item_distributor_list=[]
    item_distributor={}
    item_foodClassification_list=[]
    item_foodClassification={}
    distributor_next={}
    foodCategory_next={}
    foodCategory_value=""

    # update page number
    n=n+1

    for element in page_layout:
        
        # get only text container
        if isinstance(element, LTTextContainer):

            # skip header and footer
            if(((n==1 and element.y1 <= FIRSTPAGETOP_Y1) or (n>1 and element.y1 <= PAGETOP_Y1))
               and element.y1 > FOOTER_Y1):

                # Add all text appear in x0=20 as distributor
                # assume following text are same distributor related information, possible to be in different text box order but with fixed x0
                if element.x0 == 20:
                    newdistributor=True
                    distributor_name=element.get_text().strip().replace('\n', '')
                    distributor_y1=element.y1

                if newdistributor:
                    if element.x0 == REGNO_X0 and element.get_text().strip() != "Registered":
                        distributor_regNo=element.get_text().strip().replace('\n', '')
                    if element.x0 == ADDRESS_X0:
                        distributor_address=element.get_text().strip().replace('\n', '')
                    if element.x0 == TELNO_X0:
                        distributor_TelNo=element.get_text().strip().replace('\n', '')
                    if(distributor_regNo and distributor_address and distributor_TelNo):
                        newdistributor=False
                        distributor_list.append({
                            "y1":element.y1,
                            "distributor_name":distributor_name,
                            "distributor_regNo":distributor_regNo,
                            "distributor_address":distributor_address,
                            "distributor_TelNo":distributor_TelNo,
                            })
                        distributor_regNo=""
                        distributor_address=""
                        distributor_TelNo=""

                
                if element.x0 >= ITEM_X0:
                    
                    # get food category, it is possible to be merged with importer value in next line
                    # if it is merged, trim the value from food category and additionally add to importer list
                    if element.x0 == ITEM_X0 and element.width > YESNO_WIDTH:
                        foodCategory_value = element.get_text().strip().replace('\n', '')
                        if "No" in foodCategory_value:
                            item_importer_list.append({
                                "y1":element.y1,
                                "value":"No",
                            })
                            foodCategory_value = foodCategory_value.rstrip("No")
                        if "Yes" in foodCategory_value:
                            item_importer_list.append({
                                "y1":element.y1,
                                "value":"Yes",
                            })
                            foodCategory_value = foodCategory_value.rstrip("Yes")
                            
                        foodCategory_list.append({
                            "y1":element.y1,
                            "value":foodCategory_value,
                        })

                        # adding dummy row for Miscellaneous category
                        if "Miscellaneous" in foodCategory_value:
                            item_importer_list.append({
                                "y1":element.y1,
                                "value":"",
                            })
                            item_distributor_list.append({
                                "y1":element.y1,
                                "value":"",
                            })
                            item_foodClassification_list.append({
                                "y1":element.y1,
                                "value":"",
                            })
                    # importer, distributor and food classification text are close that
                    # importer and distributor value of next line can appear before distributor or food classification value of current line
                    # assume the text box are ordered in top down direction, put them in different list and get with FIFO order can arrange the correct listing
                    else:
                        if element.x0 == IMPORTER_X0:
                            item_importer_list.append({
                                "y1":element.y1,
                                "value":element.get_text().strip().replace('\n', ''),
                            })
                                
                        if element.x0 == DISTRIBUTOR_X0:
                            item_distributor_list.append({
                                "y1":element.y1,
                                "value":element.get_text().strip().replace('\n', ''),
                            })
                        if element.x0 == FOODCLASS_X0:
                            item_foodClassification_list.append({
                                "y1":element.y1,
                                "value":element.get_text().strip().replace('\n', ''),
                            })

    if(len(item_importer_list) != len(item_distributor_list) or len(item_importer_list) != len(item_foodClassification_list)):
        print(f"Error: item list length not match, page {n}")

    # get first distributor, keep distributor of last page if exists
    if not distributor and distributor_list:
        distributor = distributor_list.pop(0)
        foodCategory = foodCategory_list.pop(0)

    if not distributor_next and distributor_list:
        distributor_next = distributor_list.pop(0)

    # get food category, keep food category of last page if exists
    if not foodCategory and foodCategory_list:
        foodCategory = foodCategory_list.pop(0)

    if not foodCategory_next and foodCategory_list:
        foodCategory_next = foodCategory_list.pop(0)

    # getting import, distributor and food classification value in FIFO order
    for item_importer in item_importer_list:
        item_distributor=item_distributor_list.pop(0)
        item_foodClassification=item_foodClassification_list.pop(0)

        # Using next ditrubutor and food category if current item is at lower position than next distributor
        if distributor_next and distributor_next.get("y1") >= item_importer.get("y1"):
            distributor = distributor_next
            if distributor_list:
                distributor_next = distributor_list.pop(0)
            else:
                distributor_next = {}

            # new distributor always starts with new category
            if foodCategory_list:
                foodCategory = foodCategory_next
            if foodCategory_list:
                foodCategory_next = foodCategory_list.pop(0)
            else:
                foodCategory_next={}

        # Using food category if current item is at lower position than next food category
        if foodCategory_next and foodCategory_next.get("y1") >= item_importer.get("y1"):
            foodCategory = foodCategory_next
            if foodCategory_list:
                foodCategory_next = foodCategory_list.pop(0)
            else:
                foodCategory_next={}
            
        # add to data array for CSV export
        data.append([distributor.get("distributor_name"), 
                        distributor.get("distributor_regNo"),
                        distributor.get("distributor_address"),
                        distributor.get("distributor_TelNo"),
                        foodCategory.get("value"),
                        item_importer.get("value"),
                        item_distributor.get("value"),
                        item_foodClassification.get("value")])
    
    # get the last distributor, scenario when new distributor is the bottom value and no item listed yet
    if distributor_next:
        distributor = distributor_next
    
    # get the last food category, scenario when new category is the bottom value and no item listed yet
    if foodCategory_next:
        foodCategory = foodCategory_next

    if not (n % 1000):
        print ("Processing page {n}")

# create CSV file
print("Exporting...")
with open(CSVfilename, 'w', encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    
    writer.writerow(header)
    writer.writerows(data)
    print(f"file {CSVfilename} created")
