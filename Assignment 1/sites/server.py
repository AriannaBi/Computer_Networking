from socket import *
import os
import time
import sys
import shutil

serverPort = 80
if len(sys.argv) > 1:
    if 0 <= int(sys.argv[1]) <= 65535:
        serverPort = int(sys.argv[1])
print(serverPort)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)

status = {
    "200": "200 OK",
    "201": "201 Created",
    "400": "400 Bad Request",
    "403": "403 Forbidden",
    "404": "404 Not Found",
    "405": "405 Method Not Allowed",
    "501": "501 Error Response Code",
    "505": "505 HTTP Version Not Supported"
}
MIME_img = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "ico": "image/ico"
}
MIME_tex = {
    "txt": "text/plain",
    "css": "text/css",
    "js": "text/javascript",
    "html": "text/html"
}
methods = ["GET", "PUT", "DELETE", "NTW21INFO"]
print('The server is ready to receive')


# Read the hosts and entry point file from the vhost.conf and return the host of the request and the entry point file
def read_vhost(req):
    fo = open("vhosts.conf", "r")
    line_file = fo.readlines()
    lines = req.split('\r\n')
    hostname = None
    for line in lines:
        if line.rstrip().split(':')[0] == "Host":
            hostname = line.split(':')[1][1:]
    # if HTTP version 1.1 (host existence checked before)
    if req.rstrip().split()[2] == HTTP_version + " ":
        for vhost_line in line_file:
            hostname_vhost = vhost_line.rstrip().split(',')[0]
            if hostname == hostname_vhost:
                entry_fl = vhost_line.rstrip().split(',')[1]
                member_name = vhost_line.rstrip().split(',')[2]
                member_mail = vhost_line.rstrip().split(',')[3]
                fo.close()
                return hostname, entry_fl, member_name, member_mail
    # if HTTP version 1.0
    else:
        # if host doesn't exist take the first in vhost
        if hostname is None:
            hostname = line_file[0].rstrip().split(',')[0]
            entry_fl = line_file[0].rstrip().split(',')[1]
            member_name = line_file[0].rstrip().split(',')[2]
            member_mail = line_file[0].rstrip().split(',')[3]
            fo.close()
            return hostname, entry_fl, member_name, member_mail
        # if host exists
        else:
            for vhost_line in line_file:
                hostname_vhost = vhost_line.rstrip().split(',')[0]
                if hostname == hostname_vhost:
                    entry_fl = vhost_line.rstrip().split(',')[1]
                    member_name = vhost_line.rstrip().split(',')[2]
                    member_mail = vhost_line.rstrip().split(',')[3]
                    fo.close()
                    return hostname, entry_fl, member_name, member_mail


# check better because /file return file (check for extension)
def get_mime(fname):
    mime = fname.split('/')[-1].split('.')[-1]
    return mime


def get_content_type(host_nm, fname):
    if fname == "/":
        # check what extension is the entry point
        fo = open("vhosts.conf", "r")
        line_file = fo.readlines()
        for vhost_line in line_file:
            hostname_vhost = vhost_line.rstrip().split(',')[0]
            if host_nm == hostname_vhost:
                entry_file = vhost_line.rstrip().split(',')[1]
                fo.close()
        mime_entry_point = entry_file.split(".")[0]
        content_type = "Content-Type: " + MIME_tex[mime_entry_point]
        return content_type
    mime = get_mime(fname)
    if mime in MIME_img:
        content_type = "Content-Type: " + MIME_img[mime]
        return content_type
    if mime in MIME_tex:
        content_type = "Content-Type: " + MIME_tex[mime]
        return content_type
    return None

#Here we have the function for GET request and the appropriate header response.
def GET_response(fname, host_nm, entry_point_file, HTTP_version):
    if fname == "/" or filename == "//":
        fname = host_name + "/" + entry_point_file
    else:
        fname = host_name + fname
    if not os.path.isdir(fname):
        if os.access(fname, os.F_OK):  # check existence of file
            if os.access(fname, os.R_OK):  # check readability of file
                f = open(fname, "r")
                output_data = f.read()
                f.close()
                content_type = get_content_type(host_nm, fname)
                if content_type is not None:
                    body_len = len(output_data)
                    header = HTTP_version + " " + status["200"] + "\r\n" + \
                             "Date: " + time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()) + "\r\n" + \
                             "Server: " + "Bianchi_Bettelini_Jacob" + "\r\n" + \
                             "Content-Length: " + str(body_len) + "\r\n" + \
                             content_type + "\r\n\r\n"
                else:
                    header = HTTP_version + " " + status["404"] + "\r\n\r\n"
                    return header
                response = header + output_data
                return response
            else:
                header = HTTP_version + " " + status["403"] + "\r\n\r\n"
                return header
        else:
            header = HTTP_version + " " + status["404"] + "\r\n\r\n"
            return header
    else:
        header = HTTP_version + " " + status["404"] + "\r\n\r\n"
        return header

#Here we have the function for PUT request, which can update a file also add a file and the appropriate header response.
def PUT_response(fname, host_nm, body_file, HTTP_version):
    if fname == "/" or fname == "//":  # Example /
        fname = "/" + host_nm + "/" + entry_file
    elif fname[0] == "/" and len(fname) > 2:  # Example /file.html
        fname = "/" + host_nm + fname
    if os.access(fname[1:], os.F_OK):  # check existence of file
        if os.access(fname[1:], os.R_OK) and os.access(fname[1:], os.W_OK):  # check readable and writable
            f = open(fname[1:], "r+")
            f.seek(0)
            f.truncate()
            f.write(body_file)
            f.close()
            print("ALREADY EXISTS")
        else:
            res = HTTP_version + " " + status["403"] + "\r\n\r\n"
            return res
    else:
        # if extension is not allowed, return 404
        mime = get_mime(fname)
        if mime not in MIME_tex and mime not in MIME_img:
            res = HTTP_version + " " + status["404"] + "\r\n\r\n"
            return res
        try:
            print("NOT ALREADY EXISTS")
            f = open(fname[1:], "w")
            f.write(body_file)
            f.close()
        except IOError:
            res = HTTP_version + " " + status["404"] + "\r\n\r\n"
            return res
    res = None
    content_type = get_content_type(host_nm, fname)
    if content_type is not None:
        res = HTTP_version + " " + status["201"] + "\r\n" + \
                 "Date: " + time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()) + "\r\n" + \
                 "Server: " + "Bianchi_Bettelini_Jacob" + "\r\n" + \
                 "Content-Length: " + str(len(body)) + "\r\n" + \
                 content_type + "\r\n\r\n"
    return res

#Here we have the function for DELETE request, which can delete a file or a folder and the appropriate header response.
def DELETE_method(fname, host_nm, entry_point_file, body, HTTP_version):
    if fname == "/" or fname == "//":  # Example /
        fname = host_nm + "/" + entry_point_file
    elif fname[0] == "/" and len(fname) > 2:  # Example /file.html
        fname = host_nm + fname
    try:
        if os.path.isfile(fname):
            os.remove(fname)
            print("FILE REMOVED")
        elif os.path.isdir(fname):
            shutil.rmtree(fname)
            print("FOLDER REMOVED")
        else:
            print("NO SUCH FILE EXISTS")
    except IOError:
        print("NO SUCH FILE EXISTS")
        header = HTTP_version + " " + status["404"] + "\r\n\r\n"
        return header

    content_type = get_content_type(host_nm, fname)
    if content_type is not None:
        header = HTTP_version + " " + status["200"] + "\r\n" + \
                 "Date: " + time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()) + "\r\n" + \
                 "Server: " + "Bianchi_Bettelini_Jacob" + "\r\n" + \
                 "Content-Length: " + str(len(body)) + "\r\n" + \
                 content_type + "\r\n\r\n"
    else:
        header = HTTP_version + " " + status["404"] + "\r\n\r\n"
    return header

#Here we have the NTW21INFO method that responds with the appropriate response of Date, Server, Contentlength and Content Type
def NTW21INFO_response(request, HTTP_version):
    if request.rstrip().split()[1] != "/" and request.rstrip().split()[1] != "//":
        res = HTTP_version + " " + status["400"] + "\r\n\r\n"
        return res
    temp = read_vhost(request)
    member_name = temp[2]
    host_nm = temp[0]
    member_mail = temp[3]
    body_file = "The administrator of " + host_nm + " is " + member_name + \
           ".\nYou can contact him at " + member_mail[:-1] + "."
    len_body = len(body_file)

    header = HTTP_version + " " + status["200"] + "\r\n" + \
             "Date: " + time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()) + "\r\n" + \
             "Server: " + "Bianchi_Bettelini_Jacob" + "\r\n" + \
             "Content-Length: " + str(len_body) + "\r\n" + \
             "Content-Type: text/plain" + "\r\n\r\n"
    res = header + body_file
    return res


# check that the first line is composed by 3 elements, check that the methods of the request exists
# check that if the connection is HTTP/1.1 the host is mandatory,
# check that the name of the host exists in the vhost file
def check_request_line(request, HTTP_version):
    res = None
    check = request.splitlines()
    if len(check[0].rstrip().split()) != 3:
        res = HTTP_version + " " + status["400"] + "\r\n\r\n"
    if check[0].rstrip().split()[2] == "HTTP/1.1":
        if len(check) < 2:
            res = HTTP_version + " " + status["400"] + "\r\n\r\n"
            return res
        for line in check:
            if line.split(":")[0] == "Host":
                host_nm = line.split(":")[1][1:]
                if not check_host_exists_in_vhost(host_nm):
                    res = HTTP_version + " " + status["400"] + "\r\n\r\n"
    elif check[0].rstrip().split()[0] not in methods:
        res = HTTP_version + " " + status["405"] + "\r\n\r\n"
        return res
    return res


# check if the host of the param exists in the vhost file
def check_host_exists_in_vhost(host_nm):
    fo = open("vhosts.conf", "r")
    line_file = fo.readlines()
    for line in line_file:
        if line.split(",")[0] == host_nm:
            return True
    return False


# Checks the HTTP version. Return None if it's supported, otherwise return 505 status code
def check_version_HTTP(request):
    res = None
    if request.rstrip().split()[2] != "HTTP/1.1" and request.rstrip().split()[2] != "HTTP/1.0":
        # used version 1.0 as default
        res = "HTTP/1.0 " + status["505"] + "\r\n\r\n"
    return res



while True:
    connectionSocket, addr = serverSocket.accept()
    req = connectionSocket.recv(1024).decode()
    if not req:
        #we use 1.0 as default
        response = "HTTP/1.0 " + status["400"] + "\r\n\r\n"
        connectionSocket.send(response)
        connectionSocket.close()
        break
    print(req)


    #if the first line header of the request has less than 3 arguments returns error
    if len(req.splitlines()[0].split()) < 3: # GET
        if "HTTP/1.0" in req.splitlines()[0]:
            # HTTP_version = "HTTP/1.0"
            response = "HTTP/1.0 " + status["505"] + "\r\n\r\n"
            connectionSocket.send(response)
            connectionSocket.close()
            break
        elif  "HTTP/1.1" in req.splitlines()[0]:
            # HTTP_version = "HTTP/1.1"
            response = "HTTP/1.1 " + status["505"] + "\r\n\r\n"
            connectionSocket.send(response)
            connectionSocket.close()
            if "Connection: close" in req.splitlines()[0]:
                break
        else:
            #we use 1.0 as default
            response = "HTTP/1.0 " + status["400"] + "\r\n\r\n"
            connectionSocket.send(response)
            connectionSocket.close()
            break


    # check that the HTTP version is supported (HTTP/1.1 or HTTP/1.0)
    response = check_version_HTTP(req)
    if response is not None:
        connectionSocket.send(response)
        connectionSocket.close()
        break


    if "HTTP/1.0" in req.splitlines()[0]:
        HTTP_version = "HTTP/1.0"
    elif "HTTP/1.1" in req.splitlines()[0]:
        HTTP_version = "HTTP/1.1"

    connection = False
    if HTTP_version == "HTTP/1.1":
        if "Connection: close" in req.splitlines():
            connection = True

    # check that the first line of request is fine
    response = check_request_line(req, HTTP_version)
    if response is not None:
        connectionSocket.send(response)
        connectionSocket.close()
        if (HTTP_version == "HTTP/1.1" and connection) or HTTP_version == "HTTP/1.0":
            break


    # Set host and entry point (given by request)
    vhost = read_vhost(req)
    host_name = vhost[0]  # Example: guyincognito.ch
    entry_file = vhost[1]  # Example: home.html
    response = None
    # Extract what method the request contains
    method = req.split()[0]
    if method == "GET":
        filename = req.split()[1]  # Example: / or /images/avatar.png
        response = GET_response(filename, host_name, entry_file, HTTP_version)
    elif method == "PUT":
        filename = req.split()[1]  # Example: / or /file_name.html
        body = req.split("\r\n\r\n")[1]
        response = PUT_response(filename, host_name, body, HTTP_version)
        if response is None:
            response = HTTP_version + " " + status["404"] + "\r\n\r\n"
    elif method == "NTW21INFO":
        filename = req.split()[1]
        response = NTW21INFO_response(req, HTTP_version)
    elif method == "DELETE":
        body = req.split("\r\n\r\n")[1]
        filename = req.split()[1]  # Example: / or /images/avatar.png
        response = DELETE_method(filename, host_name, entry_file, body, HTTP_version)
    else:
        response = HTTP_version + " " + status["400"] + "\r\n\r\n"


    if response is not None:
        if HTTP_version == "HTTP/1.0":
            connectionSocket.send(response)
            connectionSocket.close()
            break
        else:
            connectionSocket.send(response)
            connectionSocket.close()
            if connection:
                break
    else:
        response = HTTP_version + " " + status["501"] + "\r\n\r\n"
        if HTTP_version == "HTTP/1.0":
            connectionSocket.send(response)
            connectionSocket.close()
            break
        else:
            connectionSocket.send(response)
            connectionSocket.close()
            if connection:
                break


# References:
# https://realpython.com/python-sockets/#tcp-sockets
# https://github.com/davidshepherd7/Kurose-and-Ross-socket-programming-exercises/blob/exercises/LICENSE
# https://github.com/yuva29/client-server-model-python/blob/master/server.py
# https://github.com/matheusMoreno/kurose-sockets/blob/master/webserver/webclient.py