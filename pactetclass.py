class waterColumnDatagram():
    header = [
        ('Number_of_bytes_in_datagram', 4),
        ('Start_identifier', 1),
        ('Type_of_datagram', 1),
        ('EM_model_number', 2),
        ('Date', 4),
        ('Time_since_midnight_in_milliseconds', 4),
        ('Ping_counter', 2),
        ('System_serial_number', 2),
        ('Number_of_datagrams', 2),
        ('Datagram_numbers', 2),
        ('Number_of_transmit_sectors', 2),
        ('Total_no._of_receive_beams', 2),
        ('Number_of_beams_in_this_daragram', 2),
        ('Sound_speed_in_0.1m/s', 2),
        ('Sampling_frequency_in_0.01Hz_resolution', 4),
        ('TX_time_heave_in_cm', 2),
        ('TVG_function_applied', 1),
        ('TVG_offset_in_dB', 1),
        ('Scanning_info.', 1),
        ('Sparse', 3)
    ]

    Nrx = [
        # Ntr entries of:
        ('Ntr_Beam_pointing_angle_ref_vertical_in_0.01°', 2),
        ('Ntr_Start_range_sample_number', 2),
        ('Ntr_Number_of_samples', 2),
        ('Ntr_Detected_range_in_samples', 2),
        ('Ntr_Transmit_sector_number', 1),
        ('Ntr_Beam_number', 1)
    ]

    sample = ('Ns_Sample_amplitude_in_0.5dB_resolution', 1)

    end = [
        ('Ns_End_indentifier', 1),
        ('Ns_Check_sum_of_data_between_STX_and_ETX', 2)
    ]