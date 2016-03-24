% Decode RFID Raw data
% -- Andri Rahmadhani & Bontor Humala, March 2016

% Set parameters
fName = 'signal.txt';
% if window = 10 and threshold 0.7, stdThres = 0.03 it can be used to detect reader query
% if window = 2 and threshold 0.95, it can be used to detect tag data
window = 4;
threshold = 0.83;
stdWindow = 4;
stdThres = 0.01;

% Read RFID raw data from file
fHandle = fopen(fName);
formatData = '%f';
rawData = fscanf(fHandle, formatData);
fclose(fHandle);
rawData = rawData(2600:end);

% Create time scale
%sz = max(size(rawData)); 
%t=(0:(sz-1)).*(1e6/freqSampling);     % Time in usec

% Filter moving average
mvAvgArr = [];
for i=1:length(rawData)
    mvAvg = 0;    
    for j=i:(i+window)
        if j <= length(rawData)
            mvAvg = mvAvg + rawData(j);
        end
    end
    mvAvg = mvAvg/window;
    mvAvgArr = [mvAvgArr mvAvg];
end

figure(1);
%plot(rawData);
hold on;
plot (mvAvgArr);

% Calculate 1 tari and detect rising edges
% 1) Creating zero one graph
stdDevArr = [];
for i=1:length(mvAvgArr)
    stdDev = 0;
    if (i+stdWindow <= length(mvAvgArr))
        stdDev = std(mvAvgArr(i:i+stdWindow));
        if (stdDev > stdThres)
            stdDevArr = [stdDevArr threshold];
        else
            stdDevArr = [stdDevArr 0];
        end
    end
end
%hold on;
%plot (stdDevArr);

% 2) Find slopes
slopeArr = [0];
for i=1:length(stdDevArr)
    if (i+1 <= length(stdDevArr))
        if (stdDevArr(i) > stdDevArr(i+1)) % high slope
            slopeArr = [slopeArr -threshold];
        elseif (stdDevArr(i) < stdDevArr(i+1)) % low slope
            slopeArr = [slopeArr threshold];
        else
            slopeArr = [slopeArr 0];
        end
    end
end

%hold on;
%plot (slopeArr);

% 3) Find edges
edgeArr = zeros(1,length(slopeArr));
for i=1:length(slopeArr)
    if (slopeArr(i) == threshold) && ((i+1) < length(slopeArr)) % start of slope
        j = 1;
        while (slopeArr(i+j) ~= -threshold) && ((i+j) < length(slopeArr))
            j = j+1;
        end
        edgeIdx = i + round(j/2);
        if (mvAvgArr(edgeIdx+1) > mvAvgArr(edgeIdx-1)) % rising edge
            edgeArr(edgeIdx) = threshold;
        else
            edgeArr(edgeIdx) = -threshold;
        end
    end
end

hold on;
plot (edgeArr);

% find period
period = 17;

% Create bitstream; 2 denotes calibration
bitstream = [];
jArray = [];
prevIsZero = 0; 
for i=1:length(edgeArr)
    if (abs(edgeArr(i)) == threshold)
        j = 1;
        while (abs(edgeArr(i+j)) ~= threshold) && ((i+j) < length(edgeArr))
            j = j+1;
        end
        jArray = [jArray j];
        if ((0.4*period) < j) && ((0.65*period) > j) % zero
            if (prevIsZero == 0)
                bitstream = [bitstream 0];
                prevIsZero = 1;
            else
                prevIsZero = 0;
            end
        elseif ((0.4*period) > j) || (((0.65*period) < j) && ((1.4*period) > j))
            bitstream = [bitstream 1];
            prevIsZero = 0;
        elseif ((1.4*period) < j) && ((15*period) > j)
            bitstream = [bitstream 3];
            prevIsZero = 0;
        else
            break
        end
    elseif (prevIsZero == 1) && (abs(edgeArr(i)) == threshold)
        prevIsZero = 0;
    end
end

bitstream
jArray
