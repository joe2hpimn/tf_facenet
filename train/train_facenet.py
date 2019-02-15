# -*- coding:utf-8 -*-
# Author:  zhousf
# Date:    2019-02-15
# Description: FaceNet训练、评估、导出模型、可视化
import os
from zhousf_lib.util import file_util
import time


class FaceNet(object):
    def __init__(self,
                 data_dir,
                 gpu_with_train='',
                 eval_after_training=False,
                 pretrained_model=None,
                 image_size=160,
                 embedding_size=512,
                 max_nrof_epochs=0,
                 epoch_size=1000):
        self.logs_base_dir = os.getcwd() + '/train_dir/log/'
        self.models_base_dir = os.getcwd() + '/train_dir/train/'
        self.gpu_with_train = gpu_with_train
        self.eval_after_training = eval_after_training
        self.data_dir = data_dir
        project_dir = file_util.file_path(os.getcwd())
        self.model_dir = project_dir + '/facenet-master/src'
        # 评估数据lfw
        self.lfw_dir = self.model_dir + '/align/data/lfw/lfw_160'
        self.lfw_pairs = self.model_dir + '/align/data/lfw/pairs.txt'
        if pretrained_model is None:
            pretrained_model = self.model_dir + '/models/20180402-114759/model-20180402-114759.ckpt-275'
        self.pretrained_model = pretrained_model
        self.image_size = image_size
        self.embedding_size = embedding_size
        # 训练epoch周期数
        self.max_nrof_epochs = max_nrof_epochs
        # 每个epoch周期的训练次数
        self.epoch_size = epoch_size

    def train(self):
        lfw_dir = self.lfw_dir
        lfw_pairs = self.lfw_pairs
        # 是否训练后进行评估操作
        if not self.eval_after_training:
            lfw_dir = ''
            lfw_pairs = ''
        command_train = 'python %s/train_tripletloss.py \
                    --logs_base_dir=%s \
                    --models_base_dir=%s \
                    --data_dir=%s \
                    --image_size=%d \
                    --model_def=models.inception_resnet_v1 \
                    --optimizer=RMSPROP \
                    --embedding_size=%d \
                    --learning_rate=0.01 \
                    --weight_decay=1e-4 \
                    --max_nrof_epochs=%d \
                    --people_per_batch=6 \
                    --epoch_size=%d \
                    --pretrained_model=%s \
                    --lfw_dir=%s \
                    --lfw_pairs=%s' % (
                    self.model_dir, self.logs_base_dir, self.models_base_dir, self.data_dir,
                    self.image_size, self.embedding_size, self.max_nrof_epochs, self.epoch_size,
                    self.pretrained_model, lfw_dir, lfw_pairs)
        os.environ["CUDA_VISIBLE_DEVICES"] = self.gpu_with_train
        os.system(command_train)

    def _fetch_max_checkpoint(self):
        dirs = os.listdir(self.models_base_dir)
        max_ckpt = ''
        max_index = 0
        for dir_ckpt in dirs:
            time_stamp = int(time.mktime(time.strptime(dir_ckpt, '%Y%m%d-%H%M%S')))
            if time_stamp > max_index:
                max_index = time_stamp
                max_ckpt = dir_ckpt
        model = self.models_base_dir + max_ckpt
        print(model)
        return model, max_ckpt

    def eval(self):
        model, _ = self._fetch_max_checkpoint()
        command_eval = 'python %s/validate_on_lfw.py \
                    --lfw_dir=%s \
                    --model=%s \
                    --lfw_pairs=%s ' % (self.model_dir, self.lfw_dir, model, self.lfw_pairs)
        os.system(command_eval)

    def export(self):
        model, max_ckpt = self._fetch_max_checkpoint()
        save_pb_file = model + '/'+max_ckpt+'.pb'
        print(save_pb_file)
        command_export = 'python %s/freeze_graph.py \
                  --model_dir=%s \
                  --output_file=%s' % (self.model_dir, model, save_pb_file)
        os.system(command_export)

    def show_train(self, port=6006):
        command_show_train = 'tensorboard --logdir=%s --port=%d' % (self.logs_base_dir, port)
        os.system(command_show_train)


class TrainFaceNet(FaceNet):

    def __init__(self):
        data_dir = '/Users/zhousf/tensorflow/zhousf/tf_facenet/facenet-master/src/align/data/lfw/lfw_160'
        gpu_with_train = ''
        eval_after_training = False
        pretrained_model = None
        image_size = 160
        embedding_size = 512
        max_nrof_epochs = 1
        epoch_size = 10
        FaceNet.__init__(self,
                         data_dir=data_dir,
                         gpu_with_train=gpu_with_train,
                         eval_after_training=eval_after_training,
                         pretrained_model=pretrained_model,
                         image_size=image_size,
                         embedding_size=embedding_size,
                         max_nrof_epochs=max_nrof_epochs,
                         epoch_size=epoch_size)

