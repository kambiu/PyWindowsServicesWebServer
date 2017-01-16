import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import BaseHTTPServer
import datetime
import SocketServer

class AppHTTPServer (SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	def serve_forever(self):
		self.stop_serving = False
		while not self.stop_serving:
			self.handle_request()

	def stop (self):
		self.stop_serving = True

class HRServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			f = open("C:/iis_python_app/test.txt", "ab+")
			f.write("- Time is " + str(datetime.datetime.now()) + " " + self.path + "\n")
			f.close()
			self.send_response(200)
			self.send_header('Content-type', "text/plain")
			self.end_headers()

			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

class PyServices(win32serviceutil.ServiceFramework):
	_svc_name_ = 'PyServices'
	_svc_display_name_ = 'PyServices'

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		self.httpd = None
		socket.setdefaulttimeout(60)

	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.httpd.stop()

	def SvcDoRun(self):
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
		self.main()

	def main(self):
		self.httpd = AppHTTPServer(('', 8081), HRServerHandler)
		self.httpd.serve_forever()


if __name__ == '__main__':
	if len(sys.argv) == 1:
		servicemanager.Initialize()
		servicemanager.PrepareToHostSingle(PyServices)
		servicemanager.StartServiceCtrlDispatcher()
	else:
		win32serviceutil.HandleCommandLine(PyServices)
