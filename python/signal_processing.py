from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

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

def calculate_ratios(df, channel='AF7', window_start=2, window_duration=2, sampling_rate=256):
    """Calculate alpha/beta and theta/beta ratios for specified window."""
    print(f"\n=== Frequency Band Ratios ===")
    
    # Calculate sample indices for the window
    start_sample = int(window_start * sampling_rate)
    end_sample = int((window_start + window_duration) * sampling_rate)
    
    # Extract window data
    window_data = df[channel].iloc[start_sample:end_sample].values  # Convert to NumPy array
    
    print(f"Analyzing {window_duration}s window starting at {window_start}s")
    print(f"Channel: {channel}")
    print(f"Samples in window: {len(window_data)}")
    
    # Calculate band powers
    theta_power = calculate_band_power(window_data, sampling_rate, 'theta')
    alpha_power = calculate_band_power(window_data, sampling_rate, 'alpha')
    beta_power = calculate_band_power(window_data, sampling_rate, 'beta')
    
    print(f"\nBand Powers:")
    print(f"Theta (4-8 Hz): {theta_power:.6f}")
    print(f"Alpha (8-13 Hz): {alpha_power:.6f}")
    print(f"Beta (13-30 Hz): {beta_power:.6f}")
    
    # Calculate ratios
    alpha_beta_ratio = alpha_power / beta_power
    theta_beta_ratio = theta_power / beta_power
    
    print(f"\nRatios:")
    print(f"Alpha/Beta Ratio: {alpha_beta_ratio:.3f}")
    print(f"Theta/Beta Ratio: {theta_beta_ratio:.3f}")
    
    return alpha_beta_ratio, theta_beta_ratio