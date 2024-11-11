from db import DB
from lost_link.models.local_file import LocalFileManager
from sources.dir_scanner import DirScanner

def main():
    db = DB(r"test.db", debug=True)

    file_manager = LocalFileManager(db)
    scanner = DirScanner(file_manager)

    print(scanner.get_changed_files(r"D:\tmp\Neuer Ordner"))


    #print("Started File History AI:")
    #print("--- authenticate for graph api")
    #print("--- find and download files via api ---")
    #print("--- load files ---")
    #print("--- create embeddings ---")
    #print("--- cluster files ---")
    #print("--- create history for clusters")




if __name__ == "__main__":
    main()
