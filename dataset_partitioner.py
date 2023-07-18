# Standard libs
import logging
import os
import sys
import torchvision.models as tormodels
from torchvision import datasets, transforms
import argparse
import csv

# libs from fedscale
from fedscale.dataloaders.utils_data import get_data_transform
# FedScale model libs
from fedscale.utils.models.torch_model_provider import get_cv_model
from fedscale.dataloaders.divide_data import DataPartitioner, select_dataset

tokenizer = None

def import_libs():
    global tokenizer

    if args.task == 'nlp' or args.task == 'text_clf':
        global AdamW, AlbertTokenizer, AutoConfig, AutoModelWithLMHead, AutoTokenizer, MobileBertForPreTraining, load_and_cache_examples, mask_tokens

        from transformers import (AdamW, AlbertTokenizer, AutoConfig,
                                  AutoModelWithLMHead, AutoTokenizer,
                                  MobileBertForPreTraining)

        from fedscale.dataloaders.nlp import load_and_cache_examples, mask_tokens
        tokenizer = AlbertTokenizer.from_pretrained(
            'albert-base-v2', do_lower_case=True)
    elif args.task == 'speech':
        global numba, SPEECH, BackgroundNoiseDataset, AddBackgroundNoiseOnSTFT, DeleteSTFT, FixSTFTDimension, StretchAudioOnSTFT, TimeshiftAudioOnSTFT, ToMelSpectrogramFromSTFT, ToSTFT, ChangeAmplitude, ChangeSpeedAndPitchAudio, FixAudioLength, LoadAudio, ToMelSpectrogram, ToTensor

        import numba

        from fedscale.dataloaders.speech import SPEECH, BackgroundNoiseDataset
        from fedscale.dataloaders.transforms_stft import (AddBackgroundNoiseOnSTFT,
                                                          DeleteSTFT,
                                                          FixSTFTDimension,
                                                          StretchAudioOnSTFT,
                                                          TimeshiftAudioOnSTFT,
                                                          ToMelSpectrogramFromSTFT,
                                                          ToSTFT)
        from fedscale.dataloaders.transforms_wav import (ChangeAmplitude,
                                                         ChangeSpeedAndPitchAudio,
                                                         FixAudioLength, LoadAudio,
                                                         ToMelSpectrogram,
                                                         ToTensor)

"""def init_model():
    global tokenizer

    logging.info("Initializing the model ...")

    import_libs()

    if args.task == 'nlp':
        config = AutoConfig.from_pretrained(
            os.path.join(args.data_dir, args.model + '-config.json'))
        model = AutoModelWithLMHead.from_config(config)
        tokenizer = AlbertTokenizer.from_pretrained(
            args.model, do_lower_case=True)

        # model_name = 'google/mobilebert-uncased'
        # config = AutoConfig.from_pretrained(model_name)
        # tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        # model = MobileBertForPreTraining.from_pretrained(model_name)
        # model = AutoModelWithLMHead.from_config(config)

    elif args.task == 'speech':
        if args.model == 'mobilenet':
            from fedscale.utils.models.specialized.resnet_speech import \
                mobilenet_v2
            model = mobilenet_v2(num_classes=outputClass[args.data_set])
        elif args.model == "resnet18":
            from fedscale.utils.models.specialized.resnet_speech import \
                resnet18
            model = resnet18(
                num_classes=outputClass[args.data_set], in_channels=1)
        elif args.model == "resnet34":
            from fedscale.utils.models.specialized.resnet_speech import \
                resnet34
            model = resnet34(
                num_classes=outputClass[args.data_set], in_channels=1)
        elif args.model == "resnet50":
            from fedscale.utils.models.specialized.resnet_speech import \
                resnet50
            model = resnet50(
                num_classes=outputClass[args.data_set], in_channels=1)
        elif args.model == "resnet101":
            from fedscale.utils.models.specialized.resnet_speech import \
                resnet101
            model = resnet101(
                num_classes=outputClass[args.data_set], in_channels=1)
        elif args.model == "resnet152":
            from fedscale.utils.models.specialized.resnet_speech import \
                resnet152
            model = resnet152(
                num_classes=outputClass[args.data_set], in_channels=1)
        else:
            # Should not reach here
            logging.info('Model must be resnet or mobilenet')
            sys.exit(-1)

    else:
        if args.model_zoo == "fedscale-torch-zoo":
            if args.task == "cv":
                model = get_cv_model(name=args.model,
                                        num_classes=outputClass[args.data_set])
            else:
                raise NameError(f"Model zoo {args.model_zoo} does not exist")
        elif args.model_zoo == "torchcv":
            model = tormodels.__dict__[args.model](
                num_classes=outputClass[args.data_set])
        else:
            raise NameError(f"Model zoo {args.model_zoo} does not exist")
    return model"""


def init_dataset(args):
    import_libs()

    if args.data_set == 'Mnist':
        train_transform, test_transform = get_data_transform('mnist')

        train_dataset = datasets.MNIST(args.data_dir, train=True, download=True,
                                        transform=train_transform)
        test_dataset = datasets.MNIST(args.data_dir, train=False, download=True,
                                        transform=test_transform)

    elif args.data_set == 'cifar10':
        train_transform, test_transform = get_data_transform('cifar')
        train_dataset = datasets.CIFAR10(args.data_dir, train=True, download=True,
                                            transform=train_transform)
        test_dataset = datasets.CIFAR10(args.data_dir, train=False, download=True,
                                        transform=test_transform)

    elif args.data_set == "imagenet":
        train_transform, test_transform = get_data_transform('imagenet')
        train_dataset = datasets.ImageNet(
            args.data_dir, split='train', download=False, transform=train_transform)
        test_dataset = datasets.ImageNet(
            args.data_dir, split='val', download=False, transform=test_transform)

    elif args.data_set == 'emnist':
        test_dataset = datasets.EMNIST(
            args.data_dir, split='balanced', train=False, download=True, transform=transforms.ToTensor())
        train_dataset = datasets.EMNIST(
            args.data_dir, split='balanced', train=True, download=True, transform=transforms.ToTensor())

    elif args.data_set == 'femnist':
        from fedscale.dataloaders.femnist import FEMNIST

        train_transform, test_transform = get_data_transform('mnist')
        train_dataset = FEMNIST(
            args.data_dir, dataset='train', transform=train_transform)
        test_dataset = FEMNIST(
            args.data_dir, dataset='test', transform=test_transform)

    elif args.data_set == 'openImg':
        from fedscale.dataloaders.openimage import OpenImage

        train_transform, test_transform = get_data_transform('openImg')
        train_dataset = OpenImage(
            args.data_dir, dataset='train', transform=train_transform)
        test_dataset = OpenImage(
            args.data_dir, dataset='test', transform=test_transform)

    elif args.data_set == 'reddit':
        train_dataset = load_and_cache_examples(
            args, tokenizer, evaluate=False)
        test_dataset = load_and_cache_examples(
            args, tokenizer, evaluate=True)

    elif args.data_set == 'stackoverflow':
        from fedscale.dataloaders.stackoverflow import stackoverflow

        train_dataset = stackoverflow(args.data_dir, train=True)
        test_dataset = stackoverflow(args.data_dir, train=False)

    elif args.data_set == 'amazon':
        if args.model == 'albert':
            import fedscale.dataloaders.amazon as fl_loader
            train_dataset = fl_loader.AmazonReview_loader(
                args.data_dir, train=True, tokenizer=tokenizer, max_len=args.clf_block_size)
            test_dataset = fl_loader.AmazonReview_loader(
                args.data_dir, train=False, tokenizer=tokenizer, max_len=args.clf_block_size)

        elif args.model == 'lr':
            import fedscale.dataloaders.word2vec as fl_loader
            train_dataset = fl_loader.AmazonReview_word2vec(
                args.data_dir, args.embedding_file, train=True)
            test_dataset = fl_loader.AmazonReview_word2vec(
                args.data_dir, args.embedding_file, train=False)

    elif args.data_set == 'yelp':
        import fedscale.dataloaders.yelp as fl_loader

        train_dataset = fl_loader.TextSentimentDataset(
            args.data_dir, train=True, tokenizer=tokenizer, max_len=args.clf_block_size)
        test_dataset = fl_loader.TextSentimentDataset(
            args.data_dir, train=False, tokenizer=tokenizer, max_len=args.clf_block_size)

    elif args.data_set == 'google_speech':
        print("Loading Google Speech dataset...")
        bkg = '_background_noise_'
        data_aug_transform = transforms.Compose(
            [ChangeAmplitude(), ChangeSpeedAndPitchAudio(), FixAudioLength(), ToSTFT(), StretchAudioOnSTFT(),
                TimeshiftAudioOnSTFT(), FixSTFTDimension()])
        bg_dataset = BackgroundNoiseDataset(
            os.path.join(args.data_dir, bkg), data_aug_transform)
        add_bg_noise = AddBackgroundNoiseOnSTFT(bg_dataset)
        train_feature_transform = transforms.Compose([ToMelSpectrogramFromSTFT(
            n_mels=32), DeleteSTFT(), ToTensor('mel_spectrogram', 'input')])
        train_dataset = SPEECH(args.data_dir, dataset='train',
                                transform=transforms.Compose([LoadAudio(),
                                                                data_aug_transform,
                                                                add_bg_noise,
                                                                train_feature_transform]))
        valid_feature_transform = transforms.Compose(
            [ToMelSpectrogram(n_mels=32), ToTensor('mel_spectrogram', 'input')])
        test_dataset = SPEECH(args.data_dir, dataset='test',
                                transform=transforms.Compose([LoadAudio(),
                                                            FixAudioLength(),
                                                            valid_feature_transform]))
        print("Google Speech dataset loaded!")
    elif args.data_set == 'common_voice':
        from fedscale.dataloaders.voice_data_loader import \
            SpectrogramDataset
        train_dataset = SpectrogramDataset(audio_conf=model.audio_conf,
                                            data_dir=args.data_dir,
                                            labels=model.labels,
                                            train=True,
                                            normalize=True,
                                            speed_volume_perturb=args.speed_volume_perturb,
                                            spec_augment=args.spec_augment,
                                            data_mapfile=args.data_mapfile)
        test_dataset = SpectrogramDataset(audio_conf=model.audio_conf,
                                            data_dir=args.data_dir,
                                            labels=model.labels,
                                            train=False,
                                            normalize=True,
                                            speed_volume_perturb=False,
                                            spec_augment=False)
    else:
        logging.info('DataSet must be {}!'.format(
            ['Mnist', 'Cifar', 'openImg', 'reddit', 'stackoverflow', 'speech', 'yelp']))
        sys.exit(-1)

    return train_dataset, test_dataset

def read_lines_and_write_to_csv(input_filename, output_filename, lines):
    with open(input_filename, 'r') as input_file, open(output_filename, 'w', newline='') as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        for index, row in enumerate(csv_reader):
            # print(f"index: {index}; row: {row}")
            if index-1 in lines:
                csv_writer.writerow(row)
"""
Example 1 (Google Speech):
python dataset_partitioner.py --data_set google_speech --data_dir /mydata/FedScale/benchmark/dataset/data/google_speech/ --task speech --model resnet34 --model_zoo none --num_participants 500

Example 2 (FEMNIST):
python dataset_partitioner.py --data_set femnist --data_dir /mydata/FedScale/benchmark/dataset/data/femnist/ --task femnist --model resnet152 --model_zoo none --num_participants 3400

Example 3 (Reddit):
"""

parser = argparse.ArgumentParser()

parser.add_argument('--data_set', type=str, help='dataset name')
parser.add_argument('--data_dir', type=str, help='dataset directory')
parser.add_argument('--task', type=str, help='task name')
parser.add_argument('--model', type=str, help='model name')
parser.add_argument('--model_zoo', type=str, help='model zoo')
parser.add_argument('--num_participants', type=int, help='# of participants')
parser.add_argument('--data_map_file', type=int, help='path to client-to-data mapping file')
# parser.add_argument('--block_size', type=int, default=62)

args = parser.parse_args()

print('dataset name:', args.data_set)
print('dataset directory:', args.data_dir)

# Load dataset from file system
train_dataset, test_dataset = init_dataset(args)

print(f"instances in train dataset: {len(train_dataset)}")
print(f"instances in test dataset: {len(test_dataset)}")

outputClass = {'Mnist': 10, 'cifar10': 10, "imagenet": 1000, 'emnist': 47, 'amazon': 5,
               'openImg': 596, 'google_speech': 35, 'femnist': 62, 'yelp': 5, 'inaturalist': 1010
               }

num_class = 0
if args.data_set == "google_speech":
    num_class = outputClass['google_speech']
elif args.data_set == "femnist":
    num_class = outputClass['femnist']
elif args.data_set == 'reddit':
    num_class = 0

print(f"Number of outputClass in {args.data_set} dataset: {num_class}")

print("Data partitioner starts ...")

training_sets = DataPartitioner(
    data=train_dataset, args=args, numOfClass=num_class)
training_sets.partition_data_helper(
    num_clients=args.num_participants, data_map_file=args.data_map_file)

testing_sets = DataPartitioner(
    data=test_dataset, args=args, numOfClass=num_class, isTest=True)
testing_sets.partition_data_helper(num_clients=args.num_participants)

print(f"Number of partitions: {len(training_sets.partitions)}.")

print(f"partition[0]: {training_sets.partitions[0]}.")
print(f"partition[0][0]: {training_sets.partitions[0][0]}.")

print(f"Train dataset raw data: {train_dataset.data[training_sets.partitions[0][0]]}.")
print(f"Train dataset raw tag: {train_dataset.targets[training_sets.partitions[0][0]]}.")

print("Data partitioner completes ...")

print("\n+++++ Writing partitions to CSV files ... +++++")
train_csv_path = os.path.join(args.data_dir, 'client_data_mapping', 'train.csv')
completed = 0
if not os.path.exists("/mydata/flame_dataset/" + args.data_set):
    os.makedirs("/mydata/flame_dataset/" + args.data_set)

for i in range(len(training_sets.partitions)):
    output_filename = "client-" + str(i) + "-train.csv"
    output_path = os.path.join("/mydata/flame_dataset/", args.data_set, output_filename)
    read_lines_and_write_to_csv(train_csv_path, output_path, training_sets.partitions[i])

    if i % 100 == 0:
        completed += 100
        print(f"{completed} partitions completed, {len(training_sets.partitions) - completed} remains...")
