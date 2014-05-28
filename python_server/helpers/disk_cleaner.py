import os
import time

def remove_old_file(time_before, paths):
    """
        time_before -> long
        paths -> list

        take a paths and remove all the files created before given time
    """
    for path in paths:
        if not os.path.isdir(path):
            continue
        for file_name in os.listdir(path):
            file = os.path.join(path,file_name)
            #ignore sub paths
            if os.path.isdir(file):
                continue

            file_creation_time = os.path.getmtime(file)

            if file_creation_time < time_before:
                try:
                    #remove file
                    os.unlink(file)
                except Exception:
                    pass


if __name__ == "__main__":

    paths = [
        "/var/local/singpath_verifier/unity/out",
        "/var/local/singpath_verifier/unity/test",
        "/tmp",
        "/var/local/singpath_verifier/javaserver/jsp/tomcat/webapps/ROOT/"
    ]

    time = int(time.time()) - 60*60
    remove_old_file(time, paths)
