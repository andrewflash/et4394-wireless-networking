% Read RFID message from reader to tag (R=>T)
% -- Andri Rahmadhani & Bontor Humala, March 2016

function [bitstream, lastIdx] = readReader(rawData, startIdx, stdThreshold, stdWindow)
    
    lastIdx = startIdx;
    
    % Edge Detection
    [edgeArr] = edgeDetection(rawData, startIdx, stdThreshold, stdWindow);
    edge = 1;   % Rising = 1, falling = -1

    % Find Delimiter
    delIdx = startIdx;
    while (abs(edgeArr(delIdx)) ~= edge) % find starting point of delimiter 
        delIdx = delIdx + 1;
    end
    
    % Calculate 1 tari
    tariIdx=delIdx + 1;      % First pulse is delimiter
    while (edgeArr(tariIdx) ~= edge) % find data-0 
        tariIdx = tariIdx+1;
    end
    tariStart = tariIdx;
    tariIdx = tariIdx+1;
    while (edgeArr(tariIdx) ~= edge)
        tariIdx = tariIdx+1;
    end
    tari = tariIdx - tariStart;
    
    % Create bitstream; C denotes calibration
    bitstream = [];
    for i=startIdx:length(edgeArr)
        if (edgeArr(i) == edge)
            tariIdx = i+1;
            while ((tariIdx <= length(edgeArr) && edgeArr(tariIdx) ~= edge))
                tariIdx = tariIdx + 1;
            end
            tariCurrent = tariIdx - i;
            if  (tariCurrent > 0.9*tari) && (tariCurrent < 1.1*tari)
                bitstream = [bitstream '0'];
            elseif (tariCurrent > 1.4*tari) && (tariCurrent < 2*tari)
                bitstream = [bitstream '1'];
            elseif (tariCurrent > 2*tari) && (tariCurrent < 3*tari)
                bitstream = [bitstream 'C'];
            else
                lastIdx = i;
                break % end of 1st query
            end
        end
    end
    
    % Set edge data before startIdx and after lastIndex to zero
    edgeArr(1:startIdx-1) = 0;
    edgeArr(lastIdx+1:end) = 0;
    hold on;
    plot (edgeArr)
end