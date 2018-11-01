from twisted.internet import reactor
from twisted.web import server, resource


class PrometheusMonitoringHandler(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return ""


class PrometheusMonitoringServer(object):
    def __init__(self, port, interface):
        site = server.Site(PrometheusMonitoringHandler())
        reactor.listenTCP(port, site, interface=interface or "")
        reactor.startRunning(False)

    def iterate(self):
        print("!!!!!!")
        reactor.iterate()

monitoring_config = {"port": 8080, "interface": "127.0.0.1"}
monitoring_server = PrometheusMonitoringServer(monitoring_config["port"], monitoring_config["interface"])
while 1:
    monitoring_server.iterate()