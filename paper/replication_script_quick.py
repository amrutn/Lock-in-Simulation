#Make sure to install the SILIA package as well as the modules, 
#numpy, scipy, Pillow, matplotlib, tqdm, timeit, and colorednoise.

import SILIA
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.stats as sp
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset, inset_axes
from tqdm import tqdm
import scipy.signal
import timeit
from os import path
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib import cm
from matplotlib.ticker import FormatStrFormatter
import csv
from PIL import Image
import scipy.optimize as so
import colorednoise as cn


#Replicate Figures 2 and 3, as well as relevant results.
print('Replicating Fig. 2, 3', flush = True)
'''
Generating arrays and dictionaries to represent the time axis, channels,
and reference inputs in the correct format for SILIA. 100 channels,
5 seconds of signal where each timestep is 0.2 ms. Two reference signals with frequencies of 80 and 120Hz.
'''
time = np.arange(0, 5, 1/5000) #seconds
channels = np.arange(0, 100, 1)

frequencies = [80, 120] #Hz
references = []
for freq in frequencies:
    references.append({'time' : time, 'signal' : np.sin(2 * np.pi * freq * time)})


'''
Generating noisy input signals in the correct format for SILIA. Channels 0-20, 40-60 and 80-100
contain only Gaussian noise with a std of 1. Channels 20-40 contains a sin wave oscillating at
80Hz with an amplitude of 1 as well as the Gaussian noise and channels 60-80 contains a sin wave
oscillating at 120Hz with the same amplitude and noise.
'''
signal = {'time' : time}
sig_vals = []
for t in time:
    row = []
    for channel in channels:
        if (channel >= 0 and channel < 20) or (channel >= 40 and channel < 60) or (channel >= 80 and channel < 100):
            row.append(np.random.normal(0, 1))
        elif channel >= 20 and channel < 40:
            row.append(np.sin(2 * np.pi * frequencies[0] * t) + np.random.normal(0, 1))
        elif channel >= 60 and channel < 80:
            row.append(np.sin(2 * np.pi * frequencies[1] * t) + np.random.normal(0, 1))
    sig_vals.append(row)

signal['signal'] = sig_vals

'''
Performing Lock-in Amplification
'''
LIA = SILIA.Amplifier(0)

out = LIA.amplify(references, signal, num_windows = 4, window_size = 0.33)


'''
Plotting results
'''
intensities = signal['signal']
time = signal['time']
wavelengths = channels
viridis = cm.get_cmap('viridis')
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
x = []
for t in time:
    x += [[t for w in wavelengths]]
x = np.array(x)

y = []
for w in wavelengths:
    y += [[w for t in time]]
y = np.transpose(y)

psm = ax.pcolormesh(y, x ,intensities, cmap=viridis)
cbar = fig.colorbar(psm, ax=ax)
cbar.ax.tick_params(labelsize=15)

ax.set_xlabel("Channel")
ax.set_ylabel("Time (s)")
cbar.ax.set_ylabel("Intensity (arb. units)", labelpad = 15)
ax.set_xlim(0, 100)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label, cbar.ax.yaxis.label]):
    item.set_fontsize(17)
axins = inset_axes(ax, width="50%", height="60%", bbox_to_anchor=(0.2, 0.7, .5, .4),
               bbox_transform=ax.transAxes, loc=2, borderpad=0)
axins.pcolormesh(y, x ,intensities, cmap=viridis)
x1, x2, y1, y2 = 20, 40, 4, 4.05 # specify the limits
axins.set_xlim(x1, x2) # apply the x-limits
axins.set_ylim(y1, y2) # apply the y-limits
plt.yticks([],visible=False)
plt.xticks([],visible=False)
mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0")
axins.set_title("80Hz", fontdict = {'fontsize' : 'x-large'})

axins2 = inset_axes(ax, width="50%", height="60%", bbox_to_anchor=(0.55, 0.7, .5, .4),
               bbox_transform=ax.transAxes, loc=2, borderpad=0)
axins2.pcolormesh(y, x ,intensities, cmap=viridis)
x1, x2, y1, y2 = 60, 80, 4, 4.05 # specify the limits
axins2.set_xlim(x1, x2) # apply the x-limits
axins2.set_ylim(y1, y2) # apply the y-limits
plt.yticks([],visible=False)
plt.xticks([],visible=False)
mark_inset(ax, axins2, loc1=1, loc2=3, fc="none", ec="0")
axins2.set_title("120Hz", fontdict = {'fontsize' : 'x-large'})
plt.savefig('fig_3a.png', bbox_inches = 'tight')

fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
channels = np.arange(0, 100, 1)
sig_amps = []
noise_amps = []
i = 0
while i < 100:
    if (i<= 20) or (i >= 40 and i<= 60) or (i >= 80):
        sig_amps += [0]
    elif (i > 20 and i < 40) or (i > 60 and i < 80):
        sig_amps += [1/2]
    if (i == 20 or i == 40 or i == 60 or i == 80):
        noise_amps +=[0]
    else:
        noise_amps += [1]
    i += 1
ax.bar(channels, sig_amps, color='r', width = 1, label = "Signal")
ax.bar(channels, noise_amps,bottom=sig_amps, color='b', width = 1, label = "Noise")
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_xlabel("Channel")
ax.set_ylabel("Power")
plt.legend(bbox_to_anchor = (1, 0.5), loc = "center left", fontsize = 'x-large')
plt.savefig('fig_2.svg', bbox_inches = 'tight')



averaged = 0
formats = ['b-', 'r-', 'k-', 'g-', 'm-', 'y-']
fig, ax = plt.subplots(1, 1, figsize=(3,3))
fig.set_size_inches([3,3])

ax.errorbar(channels ,out['reference 1']['magnitudes'], yerr = out['reference 1']['magnitude stds'], capsize = 3, fmt = 'b-', label = "80Hz")
ax.errorbar(channels ,out['reference 2']['magnitudes'], yerr = out['reference 2']['magnitude stds'], capsize = 3, fmt = 'r-', label = "120Hz")
plt.legend(bbox_to_anchor = (1, 0.6), frameon = False, loc = 'center left', title = 'Signal:Noise' + r' $(1:2)$'+'\n\nReference Frequency')
plt.ylabel("Magnitude")
plt.xlabel("Channel")

for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
plt.savefig('fig_3b.svg', bbox_inches='tight')


fig, ax = plt.subplots(1, 1, figsize=(3,3))
fig.set_size_inches([3,3])
ax.errorbar(channels ,out['reference 1']['phases'], yerr = out['reference 1']['phase stds'], fmt = 'b-', capsize = 3, label = "80Hz")
ax.set_xlabel("Channel")
ax.set_ylabel("Phase (rads)")
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
plt.ylim(-7, 7)
plt.savefig('fig_3c.svg', bbox_inches='tight')

fig, ax = plt.subplots(1, 1, figsize=(3,3))
fig.set_size_inches([3,3])
ax.errorbar(channels ,out['reference 2']['phases'], yerr = out['reference 2']['phase stds'], capsize = 3, fmt = 'r-', label = "120Hz")
ax.set_xlabel("Channel")
ax.set_ylabel("Phase (rads)")
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
plt.ylim(-7, 7)
plt.savefig('fig_3d.svg', bbox_inches='tight')

'''
Computing some summary statistics on the results
'''

mags1 = out['reference 1']['magnitudes']
mags2 = out['reference 2']['magnitudes']
mags1_err = out['reference 1']['magnitude stds']
mags2_err = out['reference 2']['magnitude stds']
phase1 = out['reference 1']['phases']
phase2 = out['reference 2']['phases']
phase1_err = out['reference 1']['phase stds']
phase2_err = out['reference 2']['phase stds']

mags1_mean, mags1_var = sp.describe(mags1[20:40])[2:4]
mags2_mean, mags2_var = sp.describe(mags2[60:80])[2:4]
mags1_std = np.sqrt(mags1_var)
mags2_std = np.sqrt(mags2_var)

mags1_err = np.mean(mags1_err[20:40])
mags2_err = np.mean(mags2_err[60:80])

print('mags 80Hz mean: ' + str(mags1_mean))
print('mags 120Hz mean: ' + str(mags2_mean))
print('mags 80Hz std: ' + str(mags1_std))
print('mags 120Hz std: ' + str(mags2_std))
print('mags 80Hz predicted err: ' + str(mags1_err))
print('mags 120Hz predicted err: ' + str(mags2_err))
print('mags 80Hz no signal mean: ' + str(np.mean(mags1[0:20]) * 20/100 + np.mean(mags1[40:100]) * 60/100))
print('mags 120Hz no signal mean: ' + str(np.mean(mags2[0:40]) * 40/100 + np.mean(mags1[60:100]) * 40/100))

phase1_mean, phase1_var = sp.describe(phase1[20:40])[2:4]
phase2_mean, phase2_var = sp.describe(phase2[60:80])[2:4]
phase1_std = np.sqrt(phase1_var)
phase2_std = np.sqrt(phase2_var)

phase1_err = np.mean(phase1_err[20:40])
phase2_err = np.mean(phase2_err[60:80])

print('phase 80Hz mean: ' + str(phase1_mean))
print('phase 120Hz mean: ' + str(phase2_mean))
print('phase 80Hz std: ' + str(phase1_std))
print('phase 120Hz std: ' + str(phase2_std))
print('phase 80Hz predicted err: ' + str(phase1_err))
print('phase 120Hz predicted err: ' + str(phase2_err))


#Replicate Figure 4

print('Replicating Fig. 4', flush = True)

'''
Runtime vs Input Samples
'''

input_runtimes = {}
runtime_types = ['with fit and interp.', 'without fit with interp.', 'with fit without interp.', 'without fit and interp.']
num_samples_list = np.round(np.power(1.1, np.arange(50, 122, 1)))
num_channels = 1
num_references = 1
#Number of times to average timing result
num_averages = 20
for runtime_type in runtime_types:
    tmpRuntimes = []
    print('type : ' + runtime_type, flush = True)
    for num_samples in tqdm(num_samples_list, leave = True, position = 0):
        time = np.arange(0, num_samples, 1)
        references = [{'time' : time, 'signal' : np.sin(2 * np.pi * 1/10 * time)}]
        channels = np.arange(0, num_channels, 1)
        sig = []
        for channel in channels:
            sig.append(np.sin(2 * np.pi * 1/10 * time))
        sig = np.array(sig).T
        signal = {'time' : time, 'signal' : sig}
        LIA = SILIA.Amplifier(0, pbar = False)
        runtime = 0
        for i in range(num_averages):
            if runtime_type == 'with fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'without fit with interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'with fit without interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = True, interpolate = False)
                end = timeit.default_timer()
            elif runtime_type == 'without fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = False)
                end = timeit.default_timer()
            runtime += (end-start)
        tmpRuntimes.append(runtime/num_averages)
    input_runtimes[runtime_type] = tmpRuntimes


#Plotting the result:
formats = ['r-', 'b-', 'y-', 'k-']
fig, ax = plt.subplots(1,1,figsize = (3,3))
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)


for j, runtime_type in enumerate(runtime_types):
    ax.plot(num_samples_list/10**5, input_runtimes[runtime_type], formats[j], label = runtime_type)
plt.legend()
plt.xlabel(r'Input Samples (x$10^5$)')
plt.ylabel('Runtime (s)')
plt.savefig('fig_4c.svg', bbox_inches='tight')

'''
Runtime vs Channels
'''

channels_runtimes = {}
runtime_types = ['with fit and interp.', 'without fit with interp.', 'with fit without interp.', 'without fit and interp.']
num_channels_list = np.arange(100, 1001, 100)
num_samples = 4096
num_references = 1
#Number of times to average timing result
num_averages = 20
for runtime_type in runtime_types:
    tmpRuntimes = []
    print('type : ' + runtime_type, flush = True)
    for num_channels in tqdm(num_channels_list, leave = True, position = 0):
        time = np.arange(0, num_samples, 1)
        references = [{'time' : time, 'signal' : np.sin(2 * np.pi * 1/10 * time)}]
        channels = np.arange(0, num_channels, 1)
        sig = []
        for channel in channels:
            sig.append(np.sin(2 * np.pi * 1/10 * time))
        sig = np.array(sig).T
        signal = {'time' : time, 'signal' : sig}
        LIA = SILIA.Amplifier(0, pbar = False)
        runtime = 0
        for i in range(num_averages):
            if runtime_type == 'with fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'without fit with interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'with fit without interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = True, interpolate = False)
                end = timeit.default_timer()
            elif runtime_type == 'without fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = False)
                end = timeit.default_timer()
            runtime += (end-start)
        tmpRuntimes.append(runtime/num_averages)
    channels_runtimes[runtime_type] = tmpRuntimes


#Plotting the result:
formats = ['r-', 'b-', 'y-', 'k-']
fig, ax = plt.subplots(1,1,figsize = (3,3))
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)

for j, runtime_type in enumerate(runtime_types):
    ax.plot(num_channels_list, channels_runtimes[runtime_type], formats[j], label = runtime_type)
plt.legend()
plt.xlabel('Channels')
plt.ylabel('Runtime (s)')
plt.savefig('fig_4a.svg', bbox_inches='tight')


'''
Runtime vs Number of Frequency References
'''

ref_runtimes = {}
runtime_types = ['with fit and interp.', 'without fit with interp.', 'with fit without interp.', 'without fit and interp.']
num_channels = 1
num_samples = 4096
num_references_list = np.arange(1, 11, 1)
#Number of times to average timing result
num_averages = 20
for runtime_type in runtime_types:
    tmpRuntimes = []
    print('type : ' + runtime_type, flush = True)
    for num_references in tqdm(num_references_list, leave = True, position = 0):
        time = np.arange(0, num_samples, 1)
        references = []
        for _ in range(num_references):
            references.append({'time' : time, 'signal' : np.sin(2 * np.pi * 1/10 * time)})
        channels = np.arange(0, num_channels, 1)
        sig = []
        for channel in channels:
            sig.append(np.sin(2 * np.pi * 1/10 * time))
        sig = np.array(sig).T
        signal = {'time' : time, 'signal' : sig}
        LIA = SILIA.Amplifier(0, pbar = False)
        runtime = 0
        for i in range(num_averages):
            if runtime_type == 'with fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'without fit with interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = True)
                end = timeit.default_timer()
            elif runtime_type == 'with fit without interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = True, interpolate = False)
                end = timeit.default_timer()
            elif runtime_type == 'without fit and interp.':
                start = timeit.default_timer()
                out = LIA.amplify(references, signal, fit_ref = False, interpolate = False)
                end = timeit.default_timer()
            runtime += (end-start)
        tmpRuntimes.append(runtime/num_averages)
    ref_runtimes[runtime_type] = tmpRuntimes


#Plotting the result:
formats = ['r-', 'b-', 'y-', 'k-']
fig, ax = plt.subplots(1,1,figsize = (3,3))
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)


for j, runtime_type in enumerate(runtime_types):
    ax.plot(num_references_list, ref_runtimes[runtime_type], formats[j], label = runtime_type)
plt.legend()
plt.xlabel('Frequency References')
plt.ylabel('Runtime (s)')
plt.savefig('fig_4b.svg', bbox_inches='tight')


#Replicate Figure 5

print('Replicating Fig. 5', flush = True)

LIA = SILIA.Amplifier(0, pbar = False)

def powerFunc(x,a,n):
    #Power function used for fitting
    return a/(x)**n

#Figure 5 a, b - magnitude and phase error vs data acquisition time

#First simulating signal and averaging error on lock-in output
freq = 100 #Hz
ref_time = np.arange(0, 10, 1/2000)
num_averages = 100
samples_per_cycle = 20
references = [{'time' : ref_time, 'signal' : np.sin(2 * np.pi * freq * ref_time)}]
signal_to_noises = [0.25, 0.01]


out_dict_phase = {'error squared' : {}, 'standard error' : {}, 'cycles' : []}
out_dict_mags = {'error squared' : {}, 'standard error' : {}, 'cycles' : []}
for snr in signal_to_noises:
    err_squared_phase = []
    std_errs_phase = []
    err_squared_mags = []
    std_errs_mags = []
    cycles = []
    print('Signal to Noise: ' + str(snr))
    for num_cycles in tqdm(np.arange(20, 15000, 150),leave = True, position = 0):
        cycles.append(num_cycles)
        raw_phases = []
        raw_mags = []

        time = np.arange(0, num_cycles/freq, 1/freq * 1/samples_per_cycle)
        channels = np.arange(0, num_averages, 1)
        signal = {'time' : time}
        sig_vals = []
        for channel in channels:
            column = np.sin(2 * np.pi * freq * time) + np.random.normal(0, np.sqrt(0.5/snr),time.size)
            sig_vals.append(column)
        sig_vals = np.transpose(sig_vals)
        signal['signal'] = sig_vals
        out = LIA.amplify(references, signal)
        raw_phases = out['reference 1']['phases']
        raw_mags = out['reference 1']['magnitudes']

        nobs_phase, minmax, mean_phase, variance_phase, skewness, kurtosis = sp.describe((0-np.array(raw_phases))**2)
        nobs_mags, minmax, mean_mags, variance_mags, skewness, kurtosis = sp.describe((1-np.array(raw_mags))**2)
        
        std_err_phase = np.sqrt(variance_phase/nobs_phase)
        err_squared_phase.append(mean_phase)
        std_errs_phase.append(std_err_phase)
        std_err_mags = np.sqrt(variance_mags/nobs_mags)
        err_squared_mags.append(mean_mags)
        std_errs_mags.append(std_err_mags)
    out_dict_phase['error squared'][str(snr)] = err_squared_phase
    out_dict_phase['standard error'][str(snr)] = std_errs_phase
    out_dict_phase['cycles'] = cycles
    out_dict_mags['error squared'][str(snr)] = err_squared_mags
    out_dict_mags['standard error'][str(snr)] = std_errs_mags
    out_dict_mags['cycles'] = cycles

cycles_phase_dat = out_dict_phase
cycles_mags_dat = out_dict_mags


#Plotting fig. 5a
dat = cycles_mags_dat
cycles = np.asarray(dat['cycles'])
num_samples = cycles*samples_per_cycle
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
plt.errorbar(num_samples/10**5, dat['error squared'][str(signal_to_noises[0])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[0])]), \
    fmt='o', color='orchid', capsize = 3, label = str(signal_to_noises[0]),zorder=1)
plt.errorbar(num_samples/10**5, dat['error squared'][str(signal_to_noises[1])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[1])]), \
    fmt='ro', capsize = 3, label = str(signal_to_noises[1]),zorder=2)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_ylabel(r'Error$^2$')
ax.set_xlabel(r'Samples (x$10^5$)')
ax.set_yscale('log', base = 10)

#Performing fit
fit_params_0,cov_0=so.curve_fit(powerFunc,num_samples, dat['error squared'][str(signal_to_noises[0])])
fit_params_1,cov_1=so.curve_fit(powerFunc,num_samples, dat['error squared'][str(signal_to_noises[1])])

print('Fit Parameters for 0.25 SNR (Magnitude):',flush=True)
print(r'a={0}'.format(fit_params_0[0]),flush=True)
print(r'n={0}'.format(fit_params_0[1]),flush=True)

print('Fit Parameters for 0.01 SNR (Magnitude):',flush=True)
print(r'a={0}'.format(fit_params_1[0]),flush=True)
print(r'n={0}'.format(fit_params_1[1]),flush=True)

ax.plot(num_samples/10**5, powerFunc(num_samples, *fit_params_0), 'k--',zorder=3)
ax.plot(num_samples/10**5, powerFunc(num_samples, *fit_params_1), 'k--',zorder=4)
plt.ylim(10**(-5)/2, 10**(0))
plt.savefig('fig_5a.svg', bbox_inches='tight')

#Plotting fig. 5b
dat = cycles_phase_dat
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
plt.errorbar(num_samples/10**5, dat['error squared'][str(signal_to_noises[0])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[0])]), \
    fmt='o', color='orchid', capsize = 3, label = str(signal_to_noises[0]),zorder=1)
plt.errorbar(num_samples/10**5, dat['error squared'][str(signal_to_noises[1])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[1])]), \
    fmt='ro', capsize = 3, label = str(signal_to_noises[1]),zorder=2)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_xlabel(r'Samples (x$10^5$)')
ax.set_ylabel(r'Error$^2$')
ax.set_yscale('log', base = 10)
#Performing fit
fit_params_0,cov_0=so.curve_fit(powerFunc,num_samples, dat['error squared'][str(signal_to_noises[0])])
fit_params_1,cov_1=so.curve_fit(powerFunc,num_samples, dat['error squared'][str(signal_to_noises[1])])

print('Fit Parameters for 0.25 SNR (Phase):',flush=True)
print(r'a={0}'.format(fit_params_0[0]),flush=True)
print(r'n={0}'.format(fit_params_0[1]),flush=True)

print('Fit Parameters for 0.01 SNR (Phase):',flush=True)
print(r'a={0}'.format(fit_params_1[0]),flush=True)
print(r'n={0}'.format(fit_params_1[1]),flush=True)

ax.plot(num_samples/10**5, powerFunc(num_samples, *fit_params_0), 'k--',zorder=3)
ax.plot(num_samples/10**5, powerFunc(num_samples, *fit_params_1), 'k--',zorder=4)
plt.ylim(10**(-5)/2, 10**(0))
plt.savefig('fig_5b.svg', bbox_inches='tight')


#Plotting figures 5c,d

#First simulating results for various frequencies.
freqs = np.arange(25,750,25) #Hz
time = np.arange(0, 10, 1/4000)
num_averages = 100

signal_to_noises = [0.25, 0.01]


out_dict_phase = {'error squared' : {}, 'standard error' : {}, 'freqs' : freqs}
out_dict_mags = {'error squared' : {}, 'standard error' : {}, 'freqs' : freqs}
for snr in signal_to_noises:
    err_squared_phase = []
    std_errs_phase = []
    err_squared_mags = []
    std_errs_mags = []
    print('Signal to Noise: ' + str(snr))
    for freq in tqdm(freqs,leave = True, position = 0):
        references = [{'time' : time, 'signal' : np.sin(2 * np.pi * freq * time)}]
        channels = np.arange(0, num_averages, 1)
        signal = {'time' : time}
        sig_vals = []
        for column_num in range(num_averages):
            column = np.sin(2 * np.pi * freq * time) + np.sqrt(.5/snr)*cn.powerlaw_psd_gaussian(1, time.size)
            sig_vals.append(column)
        sig_vals = np.transpose(sig_vals)

        signal['signal'] = sig_vals
        out = LIA.amplify(references, signal)

        raw_phases = out['reference 1']['phases']
        raw_mags = out['reference 1']['magnitudes']

        nobs_phase, minmax, mean_phase, variance_phase, skewness, kurtosis = sp.describe((0-np.array(raw_phases))**2)
        nobs_mags, minmax, mean_mags, variance_mags, skewness, kurtosis = sp.describe((1-np.array(raw_mags))**2)
        
        std_err_phase = np.sqrt(variance_phase/nobs_phase)
        err_squared_phase.append(mean_phase)
        std_errs_phase.append(std_err_phase)
        std_err_mags = np.sqrt(variance_mags/nobs_mags)
        err_squared_mags.append(mean_mags)
        std_errs_mags.append(std_err_mags)
    out_dict_phase['error squared'][str(snr)] = err_squared_phase
    out_dict_phase['standard error'][str(snr)] = std_errs_phase

    out_dict_mags['error squared'][str(snr)] = err_squared_mags
    out_dict_mags['standard error'][str(snr)] = std_errs_mags

#Plotting fig.5c for magnitude error
dat = out_dict_mags
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
plt.errorbar(dat['freqs'], dat['error squared'][str(signal_to_noises[0])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[0])]), \
    fmt='o', color='orchid', capsize = 3, label = str(signal_to_noises[0]))
plt.errorbar(dat['freqs'], dat['error squared'][str(signal_to_noises[1])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[1])]), \
    fmt='ro', capsize = 3, label = str(signal_to_noises[1]))
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel(r'Error$^2$')
ax.set_yscale('log', base = 10)

#Performing fit
fit_params_0,cov_0=so.curve_fit(powerFunc,freqs, dat['error squared'][str(signal_to_noises[0])])
fit_params_1,cov_1=so.curve_fit(powerFunc,freqs, dat['error squared'][str(signal_to_noises[1])])

print('Fit Parameters for 0.25 SNR (Mags, Pink Noise):',flush=True)
print(r'a={0}'.format(fit_params_0[0]),flush=True)
print(r'n={0}'.format(fit_params_0[1]),flush=True)

print('Fit Parameters for 0.01 SNR (Mags, Pink Noise):',flush=True)
print(r'a={0}'.format(fit_params_1[0]),flush=True)
print(r'n={0}'.format(fit_params_1[1]),flush=True)

ax.plot(freqs, powerFunc(freqs, *fit_params_0), 'k--',zorder=3)
ax.plot(freqs, powerFunc(freqs, *fit_params_1), 'k--',zorder=4)
plt.ylim(10**(-5), 10**(1))
plt.savefig('fig_5c.svg', bbox_inches='tight')

#Plotting fig.5d for phase error
dat = out_dict_phase
fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.set_size_inches([3,3])
plt.errorbar(dat['freqs'], dat['error squared'][str(signal_to_noises[0])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[0])]), \
    fmt='o', color='orchid', capsize = 3, label = str(signal_to_noises[0]))
plt.errorbar(dat['freqs'], dat['error squared'][str(signal_to_noises[1])], \
    yerr =np.array(dat['standard error'][str(signal_to_noises[1])]), \
    fmt='ro', capsize = 3, label = str(signal_to_noises[1]))
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel(r'Error$^2$')
ax.set_yscale('log', base = 10)

#Performing fit
fit_params_0,cov_0=so.curve_fit(powerFunc,freqs, dat['error squared'][str(signal_to_noises[0])])
fit_params_1,cov_1=so.curve_fit(powerFunc,freqs, dat['error squared'][str(signal_to_noises[1])])

print('Fit Parameters for 0.25 SNR (Phase, Pink Noise):',flush=True)
print(r'a={0}'.format(fit_params_0[0]),flush=True)
print(r'n={0}'.format(fit_params_0[1]),flush=True)

print('Fit Parameters for 0.01 SNR (Phase, Pink Noise):',flush=True)
print(r'a={0}'.format(fit_params_1[0]),flush=True)
print(r'n={0}'.format(fit_params_1[1]),flush=True)

ax.plot(freqs, powerFunc(freqs, *fit_params_0), 'k--',zorder=3)
ax.plot(freqs, powerFunc(freqs, *fit_params_1), 'k--',zorder=4)
plt.ylim(10**(-5), 10**(1))

plt.savefig('fig_5d.svg', bbox_inches='tight')

#Figure 5e

duty_cycles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
LIA = SILIA.Amplifier(0)
freq = 100 #Hz
time = np.arange(0, 15, 1/2020)
references = [{'time' : time, 'signal' : np.sin(2 * np.pi * freq * time)}]
out = []
for duty in duty_cycles:
    signal = {'time' : time, 'signal' : scipy.signal.square(2 * np.pi * freq * time, duty)/2}
    mag_out = LIA.amplify(references, signal)['reference 1']['magnitudes']
    out.append(mag_out)
    
fig, ax = plt.subplots(1, 1, figsize=(3,3))

ax.scatter(np.array(duty_cycles), out, s = 64,  c = 'b')
x = np.arange(0, 1, 0.01)
y = 2/np.pi * np.sin(np.pi * x)
ax.plot(x, y, 'r')
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
ax.set_xlabel("Duty Cycle")
ax.set_ylabel("Magnitude")
plt.savefig('fig_5e.svg', bbox_inches='tight')


#Figure 5f

frequencies = np.arange(95, 105, 0.1)
LIA = SILIA.Amplifier(0, pbar = False)
ref_freq = 100 #Hz
time = np.arange(0, 16.67, 1/2020)
references = [{'time' : time, 'signal' : np.sin(2 * np.pi * ref_freq * time)}]
cutoffs = [0.06,1.02]

filter_response = {}
for cutoff in cutoffs:
    LIA.update_cutoff(cutoff)
    outs = []
    print('Cutoff ' + str(cutoff) + ':')
    for freq in tqdm(frequencies):
        signal = {'time' : time, 'signal' : np.sin(2 * np.pi * freq * time)}
        mag_out = LIA.amplify(references, signal)['reference 1']['magnitudes']
        outs.append(mag_out)
    filter_response[cutoff] = outs
    
    
    
fig, ax = plt.subplots(1, 1, figsize=(3, 3))

plt.plot(frequencies, filter_response[cutoffs[0]], 'b-')
plt.plot(frequencies, filter_response[cutoffs[1]], 'r-')
ax.set_xlabel("Signal Frequency (Hz)")
ax.set_ylabel("Magnitude")
custom_lines = [Line2D([0], [0], color = 'w', marker = 'o', markerfacecolor='blue',\
                       markersize = 10, lw=0, linestyle = 'None'), \
                Line2D([0], [0], color = 'w', marker='o', markerfacecolor='red',\
                       markersize = 10, lw=0, linestyle = 'None')]
plt.legend(custom_lines, ['0.06', '1.02'], title = '  Cutoff (Hz)', bbox_to_anchor = [1, .5])
ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(15)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(17)
plt.ylim(0, 1.1)
plt.savefig('fig_5f.svg', bbox_inches='tight')



#Replicating Fig. 9

print('Replicating Fig. 9', flush = True)

#Fig. 9a, b, c
sampling_rate = 1000 #Hz
sim_time = .5 #second
#Time axis
time = np.arange(0, sim_time, 1/sampling_rate)
#Frequency (Hz)
freqs = [100, 75]

references = [{'time' : time, 'signal' : scipy.signal.square(2 * np.pi * freq * time)} for freq in freqs]


image1 = Image.open('FluorescentCells.jpg').convert('RGB')
arr1 = np.asarray(image1)
image1.save('fig_9a.png')

image2 = Image.open('lymph_node.jpg').convert('RGB')
arr2 = np.asarray(image2)[:512,:512]
image2 = Image.fromarray(np.uint8(arr2))
image2.save('fig_9b.png')

clean_signal = []
for t in tqdm(time):
    clean_signal.append((0.5 * scipy.signal.square(2 * np.pi * freqs[0] * t) + 0.5) * arr1\
    	+ (0.5 * scipy.signal.square(2 * np.pi * freqs[1] * t) + 0.5) * arr2)
clean_signal = np.asarray(clean_signal)
#Adding the time axis to our data
dat = {'time' : time}
dat['signal'] = clean_signal


#Displaying when both samples are fluorescing
img_mixed = Image.fromarray(np.uint8(clean_signal[0]))
img_mixed.save('fig_9c.png')


mean = 0
standard_deviation = 75
noisy_signal = np.random.normal(mean, standard_deviation, clean_signal.shape) + clean_signal
dat['signal'] = noisy_signal


#Displaying when both samples are fluorescing
img_noisy = Image.fromarray(np.uint8(noisy_signal[0]))
img_noisy.save('fig_9d.png')


LIA = SILIA.Amplifier(0)
out = LIA.amplify(references, dat, fit_ref = True, interpolate = False)

corrected1 = (np.pi/2) * np.asarray(out['reference 1']['magnitudes'])
corrected1[corrected1 > 255] = 255
img = Image.fromarray(np.uint8(corrected1))
img.save('fig_9e.png')

corrected2 = (np.pi/2) * np.asarray(out['reference 2']['magnitudes'])
corrected2[corrected2 > 255] = 255
img = Image.fromarray(np.uint8(corrected2))
img.save('fig_9f.png')