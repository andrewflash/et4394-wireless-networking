% Decode RFID Raw data
% -- Andri Rahmadhani & Bontor Humala, March 2016

% Set parameters
fName = 'signal.txt';
window = 10;

% Read RFID raw data from file
fHandle = fopen(fName);
formatData = '%f';
rawData = fscanf(fHandle, formatData);
fclose(fHandle);

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

% Detecting delimiter
% 1) Creating zero one graph
stdWindow = 10;
stdDevArr = [];
stdThres = 0.03;
for i=1:length(mvAvgArr)
    stdDev = 0;
    if (i+stdWindow <= length(mvAvgArr))
        stdDev = std(mvAvgArr(i:i+stdWindow));
        if (stdDev > stdThres) 
            stdDevArr = [stdDevArr 0.7];
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
            slopeArr = [slopeArr -0.7];
        elseif (stdDevArr(i) < stdDevArr(i+1)) % low slope
            slopeArr = [slopeArr 0.7];
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
    if (slopeArr(i) == 0.7) && ((i+1) < length(slopeArr)) % start of slope
        j = 1;
        while (slopeArr(i+j) ~= -0.7) && ((i+j) < length(slopeArr))
            j = j+1;
        end
        edgeIdx = i + round(j/2);
        if (mvAvgArr(edgeIdx+1) > mvAvgArr(edgeIdx-1)) % rising edge
            edgeArr(edgeIdx) = 0.7;
        else
            edgeArr(edgeIdx) = -0.7;
        end
    end
end

hold on;
plot (edgeArr);

% Edge Detection