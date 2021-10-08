import csv
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm


def Recipe(url):
    # print(url)
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    title = []
    thumb = []

    ingred_name = []
    ingred_amount = []
    
    recipe_step = []
    recipe_image = []

    views = []

    writer = ''

    # Title
    res = soup.find('div', 'view2_summary')
    res = res.find('h3')
    title.append(res.get_text())

    # Main_Image
    images = soup.find_all("img", attrs={"id": "main_thumbs"})
    for image in images:
        image_url = image["src"]
        thumb.append(image_url)

    # Ingred_name
    b_ = soup.find_all("b", attrs={"class": "ready_ingre3_tt"})
    try:
        for b in b_:
            ingre_list = b.find_next_siblings("a")
            for ingre in ingre_list:
                name = ingre.li.get_text()
                split_name = name.split(" ", 1)
                ingred_name.append(split_name[0])
    except (AttributeError):
        return

    # Ingred_amount
    b_ = soup.find_all("b", attrs={"class": "ready_ingre3_tt"})
    try:
        for b in b_:
            ingre_list = b.find_next_siblings("a")
            for ingre in ingre_list:
                ingred_amount.append(ingre.li.span.get_text())
    except (AttributeError):
        return

    # Recipe_Step
    res = soup.find('div', 'view_step')
    i = 0
    for n in res.find_all('div', 'view_step_cont'):
        i = i + 1
        recipe_step.append(n.get_text().replace('\n', '\n\n'))

    # Recipe_Image
    res = soup.find('div', 'view_step')
    i = 0
    for n in res.find_all('div', 'view_step_cont'):
        i = i + 1
        img = n.find("img")
        if img != None:
            img_src = img.get("src")
        else:
            img_src = ''
        recipe_image.append(img_src)
        # recipe_image.append('#' + str(i) + ':' + img_src)

    # Views
    res = soup.find('div', 'view_cate_num')
    views = int(res.get_text().replace(',', ''))


    # *** Added *** 
    # ingredients
    ingredients = []
    b_ = soup.find_all("b", attrs={"class": "ready_ingre3_tt"})
    try:
        for b in b_:
            ingre_list = b.find_next_siblings("a")
            for ingre in ingre_list:
                tem = []
                name = ingre.li.get_text()
                split_name = name.split(" ", 1)
                tem.append(split_name[0])
                tem.append(ingre.li.span.get_text())
                ingredients.append(tem)
    except (AttributeError):
        return

    # Steps
    steps  = []
    res = soup.find('div', 'view_step')
    i = 0
    for n in res.find_all('div', 'view_step_cont'):
        i = i + 1
        tem = []
        tem.append(str(i))
        tem.append(n.get_text().replace('\n', '\n\n'))

        img = n.find("img")
        if img != None:
            img_src = img.get("src")
        else:
            img_src = ''
        tem.append(img_src)
        steps.append(tem)

    # writer
    writer = int(0)

    if recipe_step and ingred_name:
        recipe = [title, thumb, writer, ingredients,
                  steps, views]
        # recipe = [title, thumb, ingred_name, ingred_amount,
        #           recipe_step, recipe_image, views, writer]
    else:
        recipe = []

    return recipe


def Search(name):
    url = "https://www.10000recipe.com/recipe/list.html?q=" + name
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    recipe_url = []

    a = soup.find("ul", attrs={"class": "common_sp_list_ul ea4"})
    links = a.find_all("div", attrs={"class": "common_sp_thumb"})

    for link in links:
        # print(link.a["href"])
        recipe_url.append('https://www.10000recipe.com' + link.a["href"])

    recipe_all = []
    for u in tqdm(recipe_url, desc=name):
        recipe = Recipe(u)
        if recipe:
            recipe_all.append(recipe)

    recipe_all_len = len(recipe_all)
    print('\t' + name + ' ' + str(recipe_all_len) + ' generated')

    return recipe_all, recipe_all_len


def save_as_file(result, json_file, csv_file, is_header):
    data = dict()
    index = 0
    for recipe in result:
        tem = dict()
        tem["title"] = recipe[0][0]
        tem["thumb"] = recipe[1]
        tem["writer"] = recipe[2]
        tem["ingredients"] = recipe[3]
        tem["steps"] = recipe[4]
        tem["views"] = recipe[5]
        
        data[str(index)] = tem
        index += 1

    # json file writing
    json.dump(data, json_file, ensure_ascii=False)

    # csv file writing
    w = csv.DictWriter(csv_file, fieldnames=data["0"].keys())
    if is_header:
        w.writeheader()

    for key in data.keys():
        w.writerow(data[key])


if __name__ == "__main__":
    # food_list = ["마늘", "양상추", "단호박", "아보카도", "쪽파", "달걀", "양파", "토마토", "당근",
    #              "콩나물", "감자", "소세지", "두부", "파프리카", "새송이버섯", "오렌지", "무"]
    food_list = ["마늘"]

    json_file = open("recipe.json", "w", encoding="utf8")
    csv_file = open("recipe.csv", "w", encoding="utf-8-sig", newline='')
    total = 0

    for i, food in enumerate(food_list):
        # try:
        #     result = Search(food)
        #     save_as_file(result, json_file, csv_file, i == 0)
        # except requests.exceptions.Timeout:
        #     print("timeout error")
        #     time.sleep(1)
        result, result_len = Search(food)
        save_as_file(result, json_file, csv_file, i == 0)
        total += result_len

    json_file.close()
    csv_file.close()

    print("[%d recipe dataset generated]" % (total))
