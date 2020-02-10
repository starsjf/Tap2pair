## Tap2pair
This is the Demo software for Tap2pair work from the papers blew.

[1] Shen J, Zhang T, Chen Y. Tap2Pair: associating wireless devices with tapping[C]//Proceedings of the 2019 ACM International Joint Conference on Pervasive and Ubiquitous Computing and Proceedings of the 2019 ACM International Symposium on Wearable Computers. ACM, 2019: 346-349.

[2] Zhang T, Yi X, Wang R, et al. Tap-to-Pair: Associating Wireless Devices with Synchronous Tapping[J]. Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, 2018, 2(4): 201.

## Abstract
This is a python script that can achieve spontaneous association with tapping from the advertising device. In this demo, the association is between wireless mouse and laptop with bluetooth. More details can be found in the above papers.

## Using example

- Firstly, modify "mouse_init" in the stdout_realtime.py into your own bluetooth mouse MAC. You can search the MAC of your mouse with "btmon".

    > mouse_init= "E7:D4:38:A5:73:CD"  --> change it into your own mouse MAC. You can scan it with pybluez.

- Secondly, using the code blew in the shell to active the script. 

     > python stdout_realtime.py -m fast

    The mode ('-m') should be 'fast' or 'slow' or 'near'. The 'fast' mode, will connect the adverting mouse with high tapping frequency. The 'low' mode, will connect the adverting mouse with low tapping frequency. The 'near' mode, will connect the adverting mouse with tapping and the RSSI of the signal is above a threshold. 

    We detect the tapping frequency by finding the peak of the FFT of the RSSI signal. When the peak FFT is in the target frequency area and the amplitude of the peak is above a target threshold. 

- Mouse controling.
    
    The mouse should be switched into adverting mode with long press. Then by typing the mouse with different patterns to achieve adverting device actived association to the target laptop.


## Configuration Settings

The laptop and wireless mouse used in this demo is: 

- Mouse : Microsoft Designer
- Laptop : DELL Precision 5520 / Thinkpad X1 carbon

This needs the python site packages blew:

- python 3.6
- numpy 
- sicpy
- bluetooth libs (install before pybluez)
    
    > sudo apt-get install libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev
	
- pybluez
    
    This package needs bluetooth lib from the drive layer. 



## FAQ

1. Why the compling failed?
    
    Please make sure all the site packages are installed correctly. Most importantly, the bluetooth library should be installed firstly.

2. Why it needs the MAC of the mouse?

    Because the mouse we used (Microsoft Designer) will change it's MAC while unbinding. It will change the forth part of the MAC by pulsing  one every time the binding changed.
    
    The script will add the mouse MAC and the MAC candidate  list to the whitelist of the BLE searching. With this method, the searching protocols can filter the adverting devices into just the target mouse.



