from cluster.common.common_node import WorkFlowCommonNode
from master.workflow.common.workflow_common import WorkFlowCommon
from master.network.nn_common_manager import NNCommonManager
from master import models
from master import serializers
import numpy as np
import operator
from PIL import Image
import io
import os
import datetime
from common.utils import *

class NeuralNetNode(WorkFlowCommonNode):
    """

    """

    def run(self, conf_data):
        """
        call on train
        :param conf_data:
        :return:
        """
        pass

    def _init_node_parm(self, pself, conf_data):
        """
        call on init parms from db
        :param node_id:
        :return:
        """
        # get initial value
        pself.conf_data = conf_data
        pself.cls_pool = conf_data["cls_pool"]
        pself.nn_id = conf_data["nn_id"]
        pself.wf_ver = conf_data["wf_ver"]
        pself.node_id = conf_data["node_id"]

        # net type
        nninfo = NNCommonManager().get_nn_id_info(conf_data["nn_id"])
        pself.net_type = nninfo[0]['fields']['dir']
        graph = NNCommonManager().get_nn_node_name(conf_data["nn_id"])
        for net in graph:
            if net['fields']['graph_node'] == 'netconf_node':
                pself.netconf_node = net['fields']['graph_node_name']
            if net['fields']['graph_node'] == 'netconf_feed':
                pself.train_feed_name = pself.nn_id + "_" + pself.wf_ver + "_" + net['fields']['graph_node_name']
            if net['fields']['graph_node'] == 'eval_feed':
                pself.eval_feed_name = pself.nn_id + "_" + pself.wf_ver + "_" + net['fields']['graph_node_name']

        pself.feed_node = pself.get_prev_node()

        # set batch
        pself.load_batch = self.get_eval_batch(pself.node_id)
        _, pself.train_batch = self.make_batch(pself.node_id)

        return pself

    def _set_progress_state(self):
        """
        set node progress info and etcs
        :return:
        """
        pass

    def predict(self, node_id, parm = {}):
        """

        :param node_id:
        :param parm:
        :return:
        """
        pass

    def eval(self, node_id, parm={}):
        """

        :param node_id:
        :param parm:
        :return:
        """
        pass

    def make_batch(self, node_id):
        """
        call this function for next version
        :param node_id:
        :return:
        """
        netnode = models.NN_WF_NODE_INFO.objects.get(nn_wf_node_id=node_id)
        nn_id = netnode.wf_state_id.nn_id
        #nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id.nn_wf_ver_id
        nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id_id
        ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        train_batch_count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id, train_flag='Y'))
        if train_batch_count == 0 :
            train_batch = None
        elif train_batch_count == 1 :
            train_batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, train_flag='Y').nn_batch_ver_id
        eval_batch_count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id, eval_flag='Y'))
        if eval_batch_count != 0 :
            eval_batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, eval_flag='Y')
            setattr(eval_batch, 'eval_flag', 'N')
            eval_batch.save()
        input_data = {}
        input_data['nn_wf_ver_id'] = ver_id
        count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id))
        input_data['nn_batch_ver_id'] = nn_id + '_' + str(nn_wf_ver_id) + '_' + str(count + 1)
        if count == 0 :
            input_data['active_flag'] = 'Y'
        else :
            input_data['active_flag'] = 'N'
        serializer = serializers.NN_VER_BATCHLIST_INFO_Serializer(data=input_data)
        if serializer.is_valid():
            serializer.save()
        return train_batch, input_data['nn_batch_ver_id']

    def get_active_batch2(self, node_id):
        """
        find batch version for predict
        :param node_id:
        :return:
        """
        netnode = models.NN_VER_WFLIST_INFO.objects.get(nn_id_id=node_id, active_flag='Y')
        #nn_id = netnode.wf_state_id.nn_id
        #nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id.nn_wf_ver_id
        #ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        count = len(models.NN_VER_WFLIST_INFO.objects.filter(nn_id_id=node_id, active_flag='Y'))
        if count == 0:
            batch = str(netnode.nn_id_id) + '_' + str(1) + str("_1")
            wf_ver = '1'
        else:
            #Todo Batch Version id로 수정 예정
            #batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, active_flag='Y').nn_batch_ver_id
            batch = str(netnode.nn_id_id) + '_' + str(netnode.nn_wf_ver_id) + str("_1")
            wf_ver= str(netnode.nn_wf_ver_id)
        return batch, wf_ver

    def get_active_batch(self, node_id):
    #     """
    #     find batch version for predict
    #     :param node_id:
    #     :return:
    #     """
    #     netnode = models.NN_VER_WFLIST_INFO.objects.get(nn_wf_node_id=node_id)
    #     nn_id = netnode.wf_state_id.nn_id
    #     nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id_id
    #     ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
    #     count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id, active_flag='Y'))
    #     if count == 0:
    #         batch = str(nn_id) + '_' + str(nn_wf_ver_id) + str("_1")
    #     else:
    #         batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, active_flag='Y').nn_batch_ver_id
    #     return batch
        netnode = models.NN_WF_NODE_INFO.objects.get(nn_wf_node_id=node_id)
        nn_id = netnode.wf_state_id.nn_id
        nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id_id
        ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id, active_flag='Y'))
        if count == 0:
            batch = str(nn_id) + '_' + str(nn_wf_ver_id) + str("_1")
        else:
            batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, active_flag='Y').nn_batch_ver_id
        return batch

    def get_eval_batch(self, node_id):
        """
        find a batch version for eval, train
        :param node_id:
        :return:
        """
        netnode = models.NN_WF_NODE_INFO.objects.get(nn_wf_node_id=node_id)
        nn_id = netnode.wf_state_id.nn_id
        nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id_id
        ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        count = len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id, eval_flag='Y'))
        if count == 0:
            batch = str(nn_id) + '_' + str(nn_wf_ver_id) + str("_1")
        else:
            batch = models.NN_VER_BATCHLIST_INFO.objects.get(nn_wf_ver_id=ver_id, eval_flag='Y').nn_batch_ver_id
        return batch

    def check_batch_exist(self, node_id):
        """
        use if you want to check batch data exists or not
        check if batch version data exists
        :param node_id:
        :return:
        """
        netnode = models.NN_WF_NODE_INFO.objects.get(nn_wf_node_id=node_id)
        nn_id = netnode.wf_state_id.nn_id
        nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id_id
        ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        if(len(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_wf_ver_id=ver_id)) > 0) :
            return True
        else :
            return False

    def save_accloss_info(self, result):
        input_data = {}
        input_data['nn_id'] = result.get_nn_id()
        input_data['nn_wf_ver_id'] = result.get_nn_wf_ver_id()
        input_data['nn_batch_ver_id'] = result.get_nn_batch_ver_id()
        #

        try:
            exists = models.TRAIN_SUMMARY_ACCLOSS_INFO.objects.filter(nn_batch_ver_id=str(input_data['nn_batch_ver_id'])).count()
            if (exists > 0):
                obj = models.TRAIN_SUMMARY_ACCLOSS_INFO.objects.get(nn_batch_ver_id=str(input_data['nn_batch_ver_id']))
                data_set1 = getattr(obj, "acc_info")
                data_set2 = getattr(obj, "loss_info")
                data_set1['acc'].append(result.acc_info['acc'][0])
                data_set2['loss'].append(result.loss_info['loss'][0])

                setattr(obj, "acc_info", data_set1)
                setattr(obj, "loss_info", data_set2)
                obj.save()
            else:
                input_data['acc_info'] = result.acc_info
                input_data['loss_info'] = result.loss_info
                serializer = serializers.TRAIN_SUMMARY_ACCLOSS_INFO_Serializer(data=input_data)
                if serializer.is_valid():
                    serializer.save()


            # input_data['acc_info'] = result.get_acc_info()
            # input_data['loss_info'] = result.get_loss_info()
            #
            #
            # obj = models.TRAIN_SUMMARY_ACCLOSS_INFO.objects.get(nn_batch_ver_id=str(input_data['nn_batch_ver_id']))
            # setattr(obj, 'acc_info', input_data['acc_info'])
            # setattr(obj, 'loss_info', input_data['loss_info'])
            # obj.save()


        except Exception as e:
            raise Exception(e)

        return input_data

    def get_before_make_batch(self, node_id, nn_batch_ver_id):
        """
        find a batch version for eval, train
        :param node_id:
        :return:
        """
        netnode = models.NN_WF_NODE_INFO.objects.get(nn_wf_node_id=node_id)
        nn_id = netnode.wf_state_id.nn_id
        nn_wf_ver_id = netnode.wf_state_id.nn_wf_ver_id.nn_wf_ver_id
        ver_id = models.NN_VER_WFLIST_INFO.objects.get(nn_id=nn_id, nn_wf_ver_id=nn_wf_ver_id).id
        _before_batch_ver_id = nn_batch_ver_id.split('_')[-1]
        for _i in range(int(_before_batch_ver_id)-1,0,-1): #find maximun version before current batch version
            before_batch_ver_id = '_'.join([nn_id,str(nn_wf_ver_id),str(_i)])
            if(models.NN_VER_BATCHLIST_INFO.objects.filter(nn_batch_ver_id=before_batch_ver_id).exists()):
                return models.NN_VER_BATCHLIST_INFO.objects.get(nn_batch_ver_id=before_batch_ver_id)
        return None

    def get_input_data(self, feed_node, cls_pool, input_feed_name):
        input_data = None
        dataconf = None

        for feed in feed_node:
            feed_name = feed.get_node_name()
            if feed_name == input_feed_name:
                data_node = feed.get_prev_node()
                for data in data_node:
                    data_name = data.get_node_name()
                    dataconf = WorkFlowCommon().get_view_obj(data_name)
                    input_data = cls_pool[feed_name]
        return input_data, dataconf


    def change_predict_fileList(self, filelist, dataconf):
        from cluster.data.data_node_image import DataNodeImage
        x_size = dataconf["preprocess"]["x_size"]
        y_size = dataconf["preprocess"]["y_size"]
        channel = dataconf["preprocess"]["channel"]

        filelist = sorted(filelist.items(), key=operator.itemgetter(0))
        file_name_arr = []
        file_data_arr = []
        try:
            for file in filelist:
                value = file[1]
                filename = file[1].name

                for img_val in value.chunks():
                    img = Image.open(io.BytesIO(img_val))

                    sess, img = DataNodeImage().image_convert(None, dataconf, img, filename, None)

                    img = img.reshape([-1, x_size, y_size, channel])
                    # img = img.flatten()

                    file_name_arr.append(filename)
                    file_data_arr.append(img)
        except Exception as e:
            print("file chagne error."+str(filename))
            print(e)

        return file_name_arr, file_data_arr

    """
    :param
    :labels : ['cat', 'dog']
    :logits : [[ 0.  1.  0.  0.  0.  0.  0.  0.  0.  0.]]
    :pred_cnt : return category count
    :return category, predict result:
    """
    def set_predict_return_cnn_img(self, labels, logits, pred_cnt):
        one = np.zeros((len(labels), 2))

        for i in range(len(labels)):
            one[i][0] = i
            one[i][1] = logits[0][i]

        onesort = sorted(one, key=operator.itemgetter(1, 0), reverse=True)
        # logging.info("############################################")
        # logging.info(onesort)
        # print("filename=" + file_name + " predict=" + labels[int(onesort[0][0])])
        # logging.info(onesort)
        data_sub = {}
        data_sub_key = []
        data_sub_val = []
        for i in range(pred_cnt):
            data_sub_key.append(labels[int(onesort[i][0])])
            val = round(onesort[i][1], 2) * 100
            if val < 0:
                val = 0
            data_sub_val.append(val)
        data_sub["key"] = data_sub_key
        data_sub["val"] = data_sub_val
        return data_sub

    def spaceprint(self, val, cnt):
        leng = len(str(val))
        cnt = cnt - leng
        restr = ""
        for i in range(cnt):
            restr += " "
        restr = restr + str(val)
        return restr

    def model_file_delete(self, model_path, modelname):
        existcnt = 10
        filelist = os.listdir(model_path)

        flist = []
        i = 0
        for filename in filelist:
            filetime = datetime.datetime.fromtimestamp(os.path.getctime(model_path + '/' + filename)).strftime(
                '%Y%m%d%H%M%S')
            tmp = [filename, filetime]
            if filename.find(modelname) > -1:
                flist.append(tmp)
            i += 1
        flistsort = sorted(flist, key=operator.itemgetter(1), reverse=True)

        for i in range(len(flistsort)):
            if i > existcnt * 3:
                os.remove(model_path + "/" + flistsort[i][0])

    def get_batch_img_data(self, data_set, type):
        labels = self.netconf["labels"]
        num_classes = len(labels)
        x_size = self.dataconf["preprocess"]["x_size"]
        y_size = self.dataconf["preprocess"]["y_size"]
        channel = self.dataconf["preprocess"]["channel"]

        labelsHot = np.zeros((num_classes, num_classes))

        for i in range(num_classes):
            for j in range(num_classes):
                if i == j:
                    labelsHot[i][j] = 1

        name_data_batch = data_set[2]
        label_data_batch = data_set[1]
        img_data_batch = data_set[0]

        if type == "T" or type == "":
            r = 0
            y_batch = np.zeros((len(label_data_batch), num_classes))
            for j in label_data_batch:
                j = j.decode('UTF-8')
                k = labels.index(j)
                y_batch[r] = labelsHot[k]
                r += 1
        else:
            y_batch = []
            for j in label_data_batch:
                j = j.decode('UTF-8')
                y_batch.append(j)

        n_batch = []
        for j in name_data_batch:
            j = j.decode('UTF-8')
            n_batch.append(j)

        try:
            x_batch = np.zeros((len(img_data_batch), len(img_data_batch[0])))
        except Exception as e:
            print(e)
        r = 0
        for j in img_data_batch:
            j = j.tolist()
            x_batch[r] = j
            r += 1

        x_batch = np.reshape(x_batch, (-1, x_size, y_size, channel))

        # logging.info("Image Label ////////////////////////////////////////////////")
        # logging.info(label_data_batch)
        # logging.info(y_batch)
        # logging.info("Image /////////////////////////////////////////////////")
        # logging.info(x_batch)

        return x_batch, y_batch, n_batch

    def _set_netconf_labels(self, input_data):
        labels = []
        while (input_data.has_next()):
            data_set = input_data[0:input_data.data_size()]
            label_data_batch = data_set[1]
            for j in label_data_batch:
                j = j.decode('UTF-8')
                try:
                    idx = labels.index(j)
                except:
                    labels.append(j)

            input_data.next()
        input_data.reset_pointer()
        self.netconf["labels"] = labels

        pred_cnt = self.netconf["param"]["predictcnt"]
        if pred_cnt > len(labels):
            pred_cnt = len(labels)

        self.netconf["config"]["num_classes"] = len(labels)
        self.netconf["param"]["predictcnt"] = pred_cnt
        self.netconf["modelpath"] = get_model_path(self.nn_id, self.net_ver, self.netconf_node)
        self.netconf["modelname"] = self.nn_id + "_" + self.net_ver

        WorkFlowCommon().set_view_obj(self.node_id, self.netconf)
        return labels
