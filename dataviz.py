
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import math
import numpy as np

import nibabel as nib
import pickle
import h5py

from nibabel.processing import resample_from_to
from make_datasets import register_MINC

workdir = '/data1/data/deepqc/'
atlas = '/data1/users/adoyle/mni_icbm152_t1_tal_nlin_asym_09a.mnc'

import subprocess
import imageio
import os

def gif_my_brain(input_file):
    t1_image = nib.load(input_file).get_data()
    print(t1_image.shape)

    plt.imshow(t1_image[:, int(t1_image.shape[1]/2), :].T, cmap='gray')

    plt.tight_layout()
    plt.axis('off')
    plt.savefig('E:/brains/andrew.png')

    x_range, y_range, z_range = t1_image.shape

    for y in range(y_range):
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,  hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        plt.imshow(t1_image[:, int(y), :].T, cmap='gray')
        plt.axis('off')
        plt.savefig('E:/brains/andrew/' + str(y) + '.png', bbox_inches='tight', pad_inches=0)

    start_slice = 202
    end_slice = 68

    images = []
    for y in range(start_slice, end_slice, -1):
        images.append(imageio.imread('E:/brains/andrew/' + str(y) + '.png'))

    for y in range(end_slice, start_slice):
        images.append(imageio.imread('E:/brains/andrew/' + str(y) + '.png'))

    imageio.mimsave('E:/brains/andrew/andrew.gif', images)

def plot_nonlinearities(output_path):

    x = np.linspace(-10.0, 10.0, 20000)

    relu = np.zeros(x.shape)
    sigmoidal = np.zeros(x.shape)
    tanh = np.zeros(x.shape)
    leakyReLu = np.zeros(x.shape)

    for i, x_ in enumerate(x):
        if x_ > 0:
            relu[i] = x_
            leakyReLu[i] = x_
        else:
            relu[i] = 0
            leakyReLu[i] = 0.1*x_

        sigmoidal[i] = sigmoid(x_)
        tanh[i] = np.tanh(x_)


    f, ax = plt.subplots(2, 2, sharex=True, sharey=True)

    ax[0][0].plot(x, sigmoidal)
    ax[0][0].set_title('$\sigma$')
    ax[0][0].grid()

    ax[0][1].plot(x, relu)
    ax[0][1].set_title('ReLU')
    ax[0][1].grid()

    ax[1][0].plot(x, tanh)
    ax[1][0].set_title('tanh')
    ax[1][0].grid()

    ax[1][1].plot(x, leakyReLu)
    ax[1][1].set_title('Leaky ReLU')
    ax[1][1].grid()

    # plt.tight_layout()

    plt.suptitle('Non-Linear Activations')

    ax[0][0].set_xlim([-3, 3])
    ax[0][0].set_ylim([-1.1, 1.1])
    plt.savefig(output_path + 'nonlinearities.png', bbox_inches='tight')

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def dataset_examples():

    root_path = '/data1/users/adoyle/'

    abide_file = root_path + '/deep_abide/resampled/50002.mnc'
    ping_file = root_path + '/PING/resampled/p0008_20100127_150603_2_mri.mnc'
    ibis_file = root_path + '/IBIS/103430/V06/mri/native/ibis_103430_V06_t1w_001.mnc'
    adni_file = root_path + '/ADNI/ADNI_002_S_0413_MR_MPRAGE_br_raw_20061117170342571_1_S22684_I30119.nii'
    ds030_file = root_path + '/ds030/sub-10159.nii.gz'

    datasets = ['ABIDE', 'PING', 'IBIS', 'ADNI', 'ds030']

    for filepath, filename in zip([abide_file, ping_file, ibis_file, adni_file, ds030_file], datasets):

        new_filepath = root_path + filepath.split('/')[-1][:-4] + '.mnc'
        if '.nii' in filepath:
            subprocess.run(['nii2mnc', filepath, new_filepath], stdout=open(os.devnull, 'wb'))
        else:
            subprocess.run(['cp', filepath, new_filepath])

        filepath = new_filepath

        # register_MINC(filepath, atlas, root_path + filename + '.mnc')

        img = nib.load(root_path + filename + '.mnc')
        print('shape:', img.shape)
        # atlas_img = nib.load(atlas)

        # if 'ADNI' in filename:
        #     t1 = img.get_data()[..., 0]
        #     img = nib.Nifti1Image(t1, np.eye(4))

        # img = resample_from_to(img, atlas_img)


        #     slice = img[img.shape[0] // 2, :, :, 0]
        # else:
        t1_data = img.get_data()
        t1_data = np.subtract(t1_data, np.min(t1_data))
        t1_data = np.divide(t1_data, np.max(t1_data))

        slice = t1_data[:, : ,t1_data.shape[2] // 2,]

        plt.close()
        plt.imshow(slice, cmap='gray', origin='lower')
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.savefig(root_path + filename + '.png', bbox_inches='tight')


def rename_abide(input_path, output_path):

    for file in os.listdir(input_path):
        print(file)
        tokens = file.split('+')
        id = tokens[1]

        print(id)
        os.rename(input_path + file, output_path + id[2:] + '.mnc')

def pass_fail_graph():

    workdir = '/home/users/adoyle/deepqc/'
    data_file = 'deepqc-allsites.hdf5'

    mri_sites = ['IBIS', 'PING', 'PITT', 'OLIN', 'OHSU', 'SDSU', 'TRINITY', 'UM', 'USM', 'YALE', 'CMU', 'LEUVEN', 'KKI',
             'NYU', 'STANFORD', 'UCLA', 'MAX_MUN', 'CALTECH', 'SBL', 'ds030']


    abide_indices = pickle.load(open(workdir + 'abide_indices.pkl', 'rb'))
    ds030_indices = pickle.load(open(workdir + 'ds030_indices.pkl', 'rb'))
    ibis_indices = pickle.load(open(workdir + 'ibis_indices.pkl', 'rb'))
    ping_indices = pickle.load(open(workdir + 'ping_indices.pkl', 'rb'))

    f = h5py.File(workdir + data_file)
    labels = f['qc_label']
    sites = f['dataset']

    passes = {}
    totals = {}
    for site in mri_sites:
        passes[site] = 0
        totals[site] = 0

    for site in mri_sites:
        for index in abide_indices:
            if site in sites[index].decode('UTF-8'):
                print(site, labels[index, ...])

                passes[site] += np.argmax(labels[index, ...])
                totals[site] += 1

    for index in ds030_indices:
        passes['ds030'] += np.argmax(labels[index, ...])
        totals['ds030'] += 1

    for index in ibis_indices:
        passes['IBIS'] += np.argmax(labels[index, ...])
        totals['IBIS'] += 1

    for index in ping_indices:
        passes['PING'] += np.argmax(labels[index, ...])
        totals['PING'] += 1

    print(passes)
    # pass_plot = [pass_fail['IBIS'], pass_fail['PING'], pass_fail['ABIDE'], pass_fail['ds030']]
    # fail_plot = [len(ibis_indices) - pass_fail['IBIS'], len(ping_indices) - pass_fail['PING'], len(abide_indices) - pass_fail['ABIDE'], len(ds030_indices) - pass_fail['ds030']]

    pass_plot, fail_plot = [], []

    for mri_site in passes:
        pass_plot.append(passes[mri_site])
        fail_plot.append(totals[mri_site] - passes[mri_site])

    # datasets = ['IBIS', 'PING', 'ABIDE', 'ds030']

    ind = np.arange(len(mri_sites))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10,4))
    ax.grid(zorder=0)

    ax.bar(ind, pass_plot, width, color='darkgreen', label='PASS', zorder=3)
    ax.bar(ind+width/2, fail_plot, width, color='darkred', label='FAIL', zorder=3)

    ax.set_ylim([0, 250])
    ax.set_xlabel('Dataset')
    ax.set_ylabel('Subjects')
    ax.set_xticks(ind + width / 4)
    ax.set_xticklabels(mri_sites)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
        item.set_fontsize(24)

    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(16)

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)

    plt.legend(shadow=True, fontsize=20, loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.tight_layout()
    plt.savefig(workdir + 'datasets-qc-pass-fail.png', bbox_inches='tight')
    plt.close()

def age_range_graph():
    workdir = '/home/users/adoyle/deepqc/'

    ibis_range = [0.5, 2]
    ping_range = [3, 20]
    abide_range = [7, 64]
    ds030_range = [21, 50]
    adni_range = [55, 95]

    start_age = [0.5, 3, 55, 7, 21]
    end_age = [2, 20, 95, 64, 50]

    age_range = []
    for i in range(len(start_age)):
        age_range.append(end_age[i] - start_age[i])

    plt.rcdefaults()
    fig, ax = plt.subplots()

    ax.grid(zorder=0)

    datasets = ['IBIS', 'PING', 'ADNI', 'ABIDE', 'ds030']
    y_pos = np.arange(len(datasets))

    ax.barh(y_pos, age_range, 0.35, left=start_age, align='center', color='darkred', zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(datasets)

    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Age Range of Subjects')
    ax.set_ylabel('Dataset')
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
        item.set_fontsize(24)

    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(20)

    plt.tight_layout()

    plt.savefig(workdir + 'ages.png')


if __name__ == '__main__':
    # age_range_graph()
    pass_fail_graph()
    # dataset_examples()

    # plot_nonlinearities('E:/')

    # gif_my_brain('E:/brains/andrew_mri_nov_2015.mnc')

    # rename_abide('E:/abide1/natives/', 'E:/abide1/abide/')

    # f = h5py.File(workdir + 'deepqc.hdf5')
    #
    # images = f['MRI']
    #
    # for i, image in enumerate(images):
    #     filename = workdir + str(i) + '.png'
    #
    #     plt.imshow(image[96, ...])
    #     plt.savefig(filename)