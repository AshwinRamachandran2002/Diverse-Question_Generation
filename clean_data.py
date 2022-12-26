import json
import scrapy
from scrapy.http import HtmlResponse

# IMPORTANT
# require json format to be in following format 
# [{ pd1category: { ... } },
#  { pd2category: { ... } },
#  ....,
#  { pd3category: { ... } }]

data = json.load(open('sample_dirty_data.json'))
answer = []
for products in data:

    # attribute tech1 cleaning
    if products["tech1"] != None:
        if products["tech1"] != "":
            response = HtmlResponse(
                url="fake", body=products["tech1"], encoding="utf-8")
            
            th_selectors = response.xpath(
                "//th").getall()#extract()  # [0].strip()
            td_selectors = response.xpath(
                "//td").getall()#extract()  # [0].strip()
            
            td_selectors_new = []
            for i in range(len(td_selectors)):
                response = HtmlResponse(
                    url="fake", body=td_selectors[i], encoding="utf-8")
                td_selectors_new.append(" ".join(response.xpath("string(//td)").extract()).strip())
            
            th_selectors_new = []
            for i in range(len(th_selectors)):
                response = HtmlResponse(
                    url="fake", body=th_selectors[i], encoding="utf-8")
                th_selectors_new.append(" ".join(response.xpath("string(//th)").extract()).strip())
            
            dict_pdt = {}
            for i in range(len(th_selectors_new)):
                dict_pdt[th_selectors_new[i].strip()] = td_selectors_new[i].strip()
            
            products["tech1"] = dict_pdt
        else:
            products["tech1"] = {}

    # attribute feature cleaning
    if products["feature"] != None:
        new_feat = []
        for feat in products["feature"]:
            # TODO: check if HTML object
            if feat != "" and feat[0] == "<":
                response = HtmlResponse(
                    url="fake", body=feat, encoding="utf-8")
                feat_cleaned = response.xpath("//span/text()").extract()
                if feat_cleaned != []:
                    key = feat_cleaned[0].strip()
                    if key in ['Shipping Weight:', 'ASIN:', 'Item model number:', 'Date first listed on Amazon:']:
                        # dict_pdt[key] = feat_cleaned[1].strip()
                        new_feat.append(key + " " + feat_cleaned[1].strip())
                    if key in ['Average Customer Review:']:
                        value = feat_cleaned[1].strip()
                        if value != "Be the first to review this item":
                            # dict_pdt[key] = feat_cleaned[4].strip()
                            new_feat.append(key + " " + feat_cleaned[4].strip())
                        else:
                            # dict_pdt[key] = "NIL"
                            new_feat.append(key + " NIL")
            else:
                if feat != "":
                    new_feat.append(feat)
        products["feature"] = new_feat#.append(dict_pdt)

    # atttribute main_cat cleaning
    if products["main_cat"] != None:
        dict_pdt = {}
        if products["main_cat"][0] == "<":
            response = HtmlResponse(
                url="fake", body=products["main_cat"], encoding="utf-8")
            src_link = response.xpath("//img/@src").extract()[0]
            alt_text = response.xpath("//img/@alt").extract()[0]
            dict_pdt["main_cat"] = [src_link, alt_text]
        else:
            dict_pdt["main_cat"] = ["NIL", products["main_cat"]]
        products["main_cat"] = dict_pdt

    # attribute description cleaning
    if products["description"] != []:
        new_desc = []
        for i in range(len(products["description"])):
            desc = products["description"][i].replace("(=^ ^=)", "").replace(
                "<br>", "").replace(
                "</br>", "").replace("<b>", "").replace("<strong>", "").replace("<br />", "").replace("</strong>", "").replace("</b>", "").replace("<b/>", "").replace("<h3>", "").replace("<I>", "").replace("<i>", "").replace("<p>", "").replace("</I>", "").replace("</h3>", "").lower().split(". ")
            for i in range(len(desc)):
                if "</a>" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<img" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<div" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<tr" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<td" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<table" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = " ".join(text)
                if "<ul>" in desc[i]:
                    response = HtmlResponse(url="fake", body=desc[i], encoding="utf-8")
                    text = response.xpath("//text()").extract()
                    desc[i] = text[0]
                    for i in range(1, len(text)):
                        desc.append(text[i])
                
                    # desc.append()
            new_desc.append(desc)
        new_desc = [item for sub in new_desc for item in sub]
        products["description"] = new_desc
        # for item in new_desc:
        #     print(item)

    # attribute fit cleaning
    if products["fit"] != None:
        if products["fit"] == "":
            products["fit"] = {}
        else:
            response = HtmlResponse(
                url="fake", body=products["fit"], encoding="utf-8")
            span_selectors = response.xpath(
                "//span/text()").extract()  # [0].strip()
            dict_pdt = {}
            for i in range(len(span_selectors)//2):
                dict_pdt[span_selectors[2*i].strip()
                         ] = span_selectors[2*i+1].strip()
            products["fit"] = dict_pdt
    
    # attribute price cleaning
    if products["price"] != None:
        if "<" in products["price"]:
            response = HtmlResponse(
                url="fake", body=products["price"], encoding="utf-8")
            span_selectors = response.xpath(
                "//span/text()").extract()
            products["price"] = " ".join(span_selectors)
    
    # attribute category cleaning
    if products["category"] != None:
        for i in range(len(products["category"])):
            if "<" in products["category"][i]:
                response = HtmlResponse(
                    url="fake", body=products["category"][i], encoding="utf-8")
                span_selectors = response.xpath(
                    "//span/text()").extract()
                products["category"][i] = " ".join(span_selectors)

    del products["date"]
    # del products["similar_item"]
    answer.append(products)

print(len(answer))
obj = json.dumps(answer)
with open('sample_clean_data.json', 'w') as f:
    f.write(obj)