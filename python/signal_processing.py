from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from config import SAMPLING_RATE

# EEG Signal Processing Functions

def calculate_band_power(data, sampling_rate, band_range):
    """Calculate power in specific frequency band using Welch's method."""
    # Define frequency bands
    freq_bands = {
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30)
    }
    
    # Calculate power spectral density
    freqs, psd = signal.welch(data, sampling_rate, nperseg=min(512, len(data)))
    
    # Find frequency indices for the band
    band_freqs = freq_bands[band_range]
    idx_band = np.logical_and(freqs >= band_freqs[0], freqs <= band_freqs[1])
    
    # Calculate band power
    band_power = np.trapezoid(psd[idx_band], freqs[idx_band])
    
    return band_power

def plot_raw_eeg(df, channel='AF7', duration=4, sampling_rate=256):
    """Plot raw EEG data for specified duration."""
    plt.figure(figsize=(12, 4))
    
    # Calculate number of samples for specified duration
    n_samples = int(duration * sampling_rate)
    
    # Get data for first N samples
    time_axis = np.arange(n_samples) / sampling_rate
    eeg_data = df[channel].iloc[:n_samples].values  # Convert to NumPy array
    
    plt.plot(time_axis, eeg_data)
    plt.title(f'Raw EEG - Channel {channel} (First {duration}s)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude (μV)')
    plt.grid(True, alpha=0.3)
    plt.show()

def compute_abr(eeg_data, fs=SAMPLING_RATE):
    """
    Compute Alpha/Beta Ratio.
    
    Args:
        eeg_data: 1D array of EEG values
        fs: sampling frequency
    
    Returns:
        abr: Alpha/Beta ratio
        alpha_power: Alpha band power
        beta_power: Beta band power
    """
    alpha_power = calculate_band_power(eeg_data, fs, band_range='alpha')
    print(f"Alpha Power: {alpha_power}")

    beta_power = calculate_band_power(eeg_data, fs, band_range='beta')
    print("Beta Power: ", beta_power)
    
    abr = alpha_power / beta_power if beta_power > 0 else 0
    
    return abr, alpha_power, beta_power