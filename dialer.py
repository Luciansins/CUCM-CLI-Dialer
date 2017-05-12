#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from termcolor import colored
import base64
import sys
import argparse
import time
import ConfigParser
from lxml import etree
import os
import time
import re

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    pass

def main(args = None):

  # ____INIT ____:
  try:    

      line_break = "\r\n"

      config = ConfigParser.ConfigParser()
      config.read("config.txt")
      server_address = str(config.get("config_set", "server_address"))
      mac_address = str(config.get("config_set", "mac_address"))
      end_user = str(config.get("config_set", "end_user"))
      end_password = str(config.get("config_set", "end_password"))
      line_number = str(config.get("config_set", "line_number"))
      fac = str(config.get("config_set", "FAC"))
      time_set = int(config.get("config_set", "hang_up_time"))
      number_list_raw = str(config.get("lists", "list"))
      number_list = number_list_raw.split(', ')    
      preffix = str(config.get("config_set", "preffix"))
      user = config.get("config_set", "user")
      password = config.get("config_set", "password")
      authentication = base64.b64encode('user:password')
      fac_suffix = '#'+fac    


      cucmWebDialUrl = 'https://'+server_address+'/webdialer/services/WebdialerSoapService70'

      

      #----------HEADERS----------    

      headers = {
        'SoapAction':'CUCM:DB ver=9.1',
        'Authorization': 'Basic ' +authentication, 
        'Content-Type': 'text/xml; charset=utf-8'
      }   




            #----------SOAP OBJECTS----------   
      
      make_call = """<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
      xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:WD70">
      <soapenv:Header/>
      <soapenv:Body>
      <urn:makeCallSoap soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
      <in0 xsi:type="urn:Credential">
      <userID xsi:type="xsd:string">"""+end_user+"""</userID>
      <password xsi:type="xsd:string">"""+end_password+"""</password>
      </in0>
      <in1 xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{0}</in1>
      <in2 xsi:type="urn:UserProfile">
      <user xsi:type="xsd:string">"""+end_user+"""</user>
      <lineNumber xsi:type="xsd:string">1</lineNumber>
      <deviceName xsi:type="xsd:string">"""+mac_address+"""</deviceName>
      <supportEM xsi:type="xsd:boolean">false</supportEM>
      <locale xsi:type="xsd:string">?</locale>
      <dontAutoClose xsi:type="xsd:boolean">true</dontAutoClose>
      <dontShowCallConf xsi:type="xsd:boolean">false</dontShowCallConf>
      </in2>
      </urn:makeCallSoap>
      </soapenv:Body>
      </soapenv:Envelope>"""


      hang_up = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
      xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"
      xmlns:tns="urn:WebdialerSoap"
      xmlns:types="urn:WebdialerSoap/encodedTypes"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <soap:Body
      soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
      <tns:endCallSoap>
      <cred href="#id1" />
      <prof href="#id2" />
      </tns:endCallSoap>
      <tns:Credential id="id1" xsi:type="tns:Credential">
      <userID xsi:type="xsd:string">"""+end_user+"""</userID>
      <password xsi:type="xsd:string">"""+end_password+"""</password>
      </tns:Credential>
      <tns:UserProfile id="id2" xsi:type="tns:UserProfile">
      <user xsi:type="xsd:string">"""+end_user+"""</user>
      <deviceName xsi:type="xsd:string">"""+mac_address+"""</deviceName>
      <lineNumber xsi:type="xsd:string">?</lineNumber>
      <supportEM xsi:type="xsd:boolean">false</supportEM>
      <locale xsi:type="xsd:string" />
      </tns:UserProfile>
      </soap:Body>
      </soap:Envelope>"""   
      

      #other arguments
      
      def call_end(data_payload):
        request = requests.post(cucmWebDialUrl, headers=headers, verify=False, data=data_payload)
        end_response = request.text
        return end_response

      if sys.argv[1] == '--config' or sys.argv[1] =='-c':
          os.system("start "+'config.txt')
          sys.exit("Config file started")
 

      if sys.argv[1] == '--end' or sys.argv[1] == '-e':

        call_end(hang_up)
        print line_break
        print  colored('The call has been terminated','red',attrs=['bold'])
        sys.exit()

       
          

      #----------ARGUMENT PARSER---------- 

      parser = argparse.ArgumentParser(epilog= 'CUCM Command Line Dialer v.1.1 by Lucians')
      parser.add_argument("number", nargs='?', help="number to be called")
      parser.add_argument("-l","--ldi", action='store_true', help= "Prepends ldi prefix 01880 to the number string")
      parser.add_argument("-f", "--fac", action='store_true', help= "Appends a forced authorization code to the number string")
      parser.add_argument("-v", "--verbose", help="Increase verbosity level", action='store_true')
      parser.add_argument("-i", "--iterate", help="Iterate calls through a vector", action='store_true')
      parser.add_argument("-e", "--end", help="Disconnect current active call", action='store_true')
      parser.add_argument("-c", "--config", help="Access the config file", action='store_true')
      args = parser.parse_args()    



      #----------FUNCTIONS----------    

      if sys.argv[1] == '--iterate' or sys.argv[1] =='-i':

        args.number = number_list[0]
        print line_break
        print 'number: ', number_list[0]
      else:
        pass

      def call_request(data_payload):

        request = requests.post(cucmWebDialUrl, headers=headers, verify=False, data=data_payload)
        this_response = request.text
        return this_response

      def __clean():

        args.number = re.sub('[^0-9]', '', args.number)
        print 'number cleaned', args.number
      if '-' in args.number or '+' in args.number:
        __clean()
      else:
        pass     

      def __ldi():

        args.number = preffix+args.number
      if args.ldi:
        __ldi()   
      

      def __fac():

        args.number = args.number+fac_suffix
      if args.fac:
        __fac()  

      #Must be after all the string manipulation  
      send_number = make_call.format(args.number)  

      response = call_request(send_number).encode('utf-8')    
      
      def _prettyXML(xml_data):

        root = etree.fromstring(xml_data)
        print(etree.tostring(root, pretty_print=True))
        


      def __verbose():

        print line_break
        print 'verbosity:', colored('ON','green',attrs=['bold'])
        print line_break
        _prettyXML(response)        

      if args.verbose:
        __verbose()


      def _responseDescription(xml_data):

        root = etree.fromstring(xml_data)
        for child in root.iter():
          if child.tag == 'responseDescription':
            if child.text == 'Success':
              print ''
              print 'Response:', colored(child.text, 'green',attrs=['bold'])
            else:
                print ''
                print 'Response:', colored(child.text, 'red',attrs=['bold'])
      

      _responseDescription(response)    

      def _responseData(xml_data):

        root = etree.fromstring(xml_data)
        for child in root.iter():
          print child.tag
          print child.text


      def iterate_call():

        time.sleep(time_set+1)
        call_request(hang_up)

        for number in number_list[1:]:
          print line_break
          print 'number:',number,
          temp_data = make_call.format(number)
          number = args.number
          response_iter = call_request(temp_data).encode('utf-8')
          _responseDescription(response_iter)

          print line_break
          time.sleep(time_set)
          call_request(hang_up)
          time.sleep(time_set/2)   
      

      if args.iterate:
        iterate_call() 


  except KeyboardInterrupt:
      print colored("\nDialer execution aborted\n","red",attrs=['bold'])

if __name__ == "__main__":
    main()
