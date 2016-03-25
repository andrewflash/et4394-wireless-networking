% Read RFID message from tag to reader (T=>R)
% -- Andri Rahmadhani & Bontor Humala, March 2016

function [bitstream, lastIdx] = readTag(rawData, startIdx, stdThreshold, stdWindow)

    % Edge Detection
    [edgeArr] = edgeDetection(rawData, startIdx, stdThreshold, stdWindow);
    edge = 1;   % Rising = 1, falling = -1
    
    % Find period, read first tag preamble, which is supposed to be 1
    tagIdx = startIdx; 
    while (abs(edgeArr(tagIdx)) ~= edge) 
        tagIdx = tagIdx+1;
    end
    tagStart = tagIdx;
    tagIdx = tagIdx+1;
    while (abs(edgeArr(tagIdx)) ~= edge)
        tagIdx = tagIdx+1;
    end
    tagPeriod = tagIdx - tagStart;

    % Create bitstream; 3 denotes 'v'
    bitstream = [];
    prevIsZero = 0; 
    for i=startIdx:length(edgeArr)
        if (abs(edgeArr(i)) == edge)
            j = 1;
            while (abs(edgeArr(i+j)) ~= edge) && ((i+j) < length(edgeArr))
                j = j+1;
            end

            if ((j >= floor(0.45*tagPeriod)) && (j <= ceil(0.55*tagPeriod))) % zero
                if (prevIsZero == 0)
                    bitstream = [bitstream '0'];
                    prevIsZero = 1;
                else
                    prevIsZero = 0;
                end
            elseif ((j > floor(0.55*tagPeriod)) && (j <= ceil(1.4*tagPeriod)))
                bitstream = [bitstream '1'];
                prevIsZero = 0;
            elseif ((j > floor(1.4*tagPeriod)) && (j <= ceil(15*tagPeriod)))
                bitstream = [bitstream 'v'];
                prevIsZero = 0;
            else
                lastIdx = i;
                break;
            end
        end
    end
    
    % Set edge data before startIdx and after lastIdx to zero
    edgeArr(1:startIdx-1) = 0;
    edgeArr(lastIdx+1:end) = 0;
    hold on;
    plot (edgeArr)
end
