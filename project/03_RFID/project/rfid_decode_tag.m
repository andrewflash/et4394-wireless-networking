% Decode RFID Raw data
% -- Andri Rahmadhani & Bontor Humala, March 2016

% Set parameters
fName = 'signal.txt';
% if window = stdWindow = 10 and threshold 0.7, stdThres = 0.03 it can be used to detect reader query
% if window = stdWindow = 4 and stdThreshold 0.01, it can be used to detect tag data
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

% Apply moving average filter to remove high frequency noise
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

% Detect rising/falling edges and calculating size of 1 Tari
% 1) Creating pulse graph. If standard variance is high, there must be a
% slope. If there is a slope, stdDevArr value is set to high. Otherwise,
% low.
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

% Detect rising/falling edges and calculating size of 1 Tari
% 2) In order to find the edge (center of the slope), we need to find the
% start and end of slope, then find the center inbetween.
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
% As mentioned previously, we find the center of the slope, which is the
% edge. If it is rising edge, value is high. If it is falling edge, value
% is negative of high (-high). Otherwise (not an edge), its zero 
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

% Create bitstream; 3 denotes v. 
bitstream = [];
%jArray = [];
prevIsZero = 0; 
for i=1:length(edgeArr)
    if (abs(edgeArr(i)) == threshold) % this is an edge
        j = 1;
        while (abs(edgeArr(i+j)) ~= threshold) && ((i+j) < length(edgeArr))
            j = j+1; % iterate until next edge
        end
        %jArray = [jArray j];
        if ((0.4*period) < j) && ((0.65*period) > j) % zero
            if (prevIsZero == 0) % new half period, must be a zero
                bitstream = [bitstream 0];
                prevIsZero = 1;
            else % previous bit is zero, this must be the other half period
                prevIsZero = 0; % ignore this other half period
            end
        elseif ((0.4*period) > j) || (((0.65*period) < j) && ((1.4*period) > j))
            bitstream = [bitstream 1];
            prevIsZero = 0;
        elseif ((1.4*period) < j) && ((15*period) > j) % 1.5*period means a v
            bitstream = [bitstream 3];
            prevIsZero = 0;
        else
            break % delimiter; end of tag backscattering
        end
    elseif (prevIsZero == 1) && (abs(edgeArr(i)) == threshold)
        prevIsZero = 0;
    end
end

%bitstream
%jArray
