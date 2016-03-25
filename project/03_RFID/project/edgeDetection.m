% Rising and falling edge detection on RFID signal
% -- Andri Rahmadhani & Bontor Humala, March 2016

function [edgeArr] = edgeDetection(rawData, startIdx, stdThres, stdWindow)
    % 1) Find slopes using standard deviation
    stdDevArr = [];
    edge = 1;
    for i=1:length(rawData)
        if (i+stdWindow <= length(rawData))
            stdDev = std(rawData(i:i+stdWindow));
            stdDevArr = [stdDevArr stdDev];            
        end
    end
    stdDevMax = max(stdDevArr);
    stdDevArr = stdDevArr.*(1/stdDevMax);   % Normalize
    stdDevArr(stdDevArr > stdThres) = edge;
    stdDevArr(stdDevArr <= stdThres) = 0;

    % 2) Find slopes
    slopeArr = [0];
    for i=1:length(stdDevArr)
        if (i+1 <= length(stdDevArr))
            if (stdDevArr(i) > stdDevArr(i+1)) % high slope
                slopeArr = [slopeArr -edge];
            elseif (stdDevArr(i) < stdDevArr(i+1)) % low slope
                slopeArr = [slopeArr edge];
            else
                slopeArr = [slopeArr 0];
            end
        end
    end

    % 3) Find edges, median of slopes
    edgeArr = zeros(1,length(slopeArr));
    for i=1:length(slopeArr)
        if (slopeArr(i) == edge) && ((i+1) < length(slopeArr)) % start of slope
            j = 1;
            while (slopeArr(i+j) ~= -edge) && ((i+j) < length(slopeArr))
                j = j+1;
            end
            edgeIdx = i + round(j/2);
            if (rawData(edgeIdx+1) > rawData(edgeIdx-1)) % rising edge
                edgeArr(edgeIdx) = edge;
            else
                edgeArr(edgeIdx) = -edge;
            end
        end
    end
 end