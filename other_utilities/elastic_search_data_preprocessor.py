import json 

def main():
    files = ["chinese_restaurants","japanese_restaurants","mexican_restaurants","indian_restaurants","italian_restaurants"]

    for filename in files:
        with open(f"C:/Users/Hp/Downloads/Personal/Personal/NYU_Course_Related/CloudComputing/{filename}.json",'r') as file:
            pydict = json.load(file)
            res = []
            for val in pydict:
                obj = {}
                obj["id"] = val["id"]
                obj["categories"] = val["categories"]
                res.append(obj)
            newfile = open(f"C:/Users/Hp/Downloads/Personal/Personal/NYU_Course_Related/CloudComputing/{filename}_os.json",'w')
            json.dump(res, newfile, indent = 4)
            
def main2():
    files = ["chinese_restaurants","japanese_restaurants","mexican_restaurants","indian_restaurants","italian_restaurants"]
    for filename in files:
        with open(f"C:/Users/Hp/Downloads/Personal/Personal/NYU_Course_Related/CloudComputing/{filename}_os.json",'r') as file:
            pydict = json.load(file)
            for val in pydict:
                try:
                    file = open(f"C:/Users/Hp/Downloads/Personal/Personal/NYU_Course_Related/CloudComputing/{filename}_aws_os.json",'x+')
                except:
                    file = open(f"C:/Users/Hp/Downloads/Personal/Personal/NYU_Course_Related/CloudComputing/{filename}_aws_os.json",'a')
                file.write('{"create": {}}\n')
                file.write(f"{json.dumps(val)}\n")
                
    

if __name__ == "__main__":
    main()
    main2()