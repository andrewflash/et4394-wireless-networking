% Rising and falling edge detection on RFID signal
% -- Andri Rahmadhani & Bontor Humala, March 2016

function [edgeArr] = edgeDetection(rawData, startIdx, stdThres, stdWindow)
	% Detect rising/falling edges and calculating size of 1 Tari
	% 1) Creating pulse graph. If standard variance is high, there must be a
	% slope. If there is a slope, stdDevArr value is set to high. Otherwise,
	% low.
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

	% 2) In order to find the edge (center of the slope), we need to find the
	% start and end of slope, then find the center inbetween.
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

    % 3) Find edges
	% As mentioned previously, we find the center of the slope, which is the
	% edge. If it is rising edge, value is high. If it is falling edge, value
	% is negative of high (-high). Otherwise (not an edge), its zero.
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