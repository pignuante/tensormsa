import json
from rest_framework.response import Response
from rest_framework.views import APIView
from master.workflow.netconf.workflow_netconf_cnn import WorkFlowNetConfCNN

class WorkFlowNetConfCnn(APIView) :
    """

    """
    def post(self, request, nnid, ver, node):
        """
        - desc : insert data
        """
        try:
            return_data = ""
            return Response(json.dumps(return_data))
        except Exception as e:
            return_data = {"status": "404", "result": str(e)}
            return Response(json.dumps(return_data))

    def get(self, request, nnid, ver, node):
        """
        - desc : get data
        """
        try:
            input_data = json.loads(str(request.body, 'utf-8'))
            return_data = WorkFlowNetConfCNN().get_view_obj(input_data)
            return Response(json.dumps(return_data))
        except Exception as e:
            return_data = {"status": "404", "result": str(e)}
            return Response(json.dumps(return_data))

    def put(self, request, nnid, ver, node):
        """
        - desc ; update data
        """
        try:
            input_data = json.loads(str(request.body, 'utf-8'))
            return_data = WorkFlowNetConfCNN().set_view_obj(input_data)
            return Response(json.dumps(return_data))
        except Exception as e:
            return_data = {"status": "404", "result": str(e)}
            return Response(json.dumps(return_data))

    def delete(self, request, nnid, ver, node):
        """
        - desc : delete  data
        """
        try:
            return_data = ""
            return Response(json.dumps(return_data))
        except Exception as e:
            return_data = {"status": "404", "result": str(e)}
            return Response(json.dumps(return_data))
