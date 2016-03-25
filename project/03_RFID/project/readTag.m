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

    % Create bitstream (1 or 0) and detect v in preamble
    bitstream = [];
    prevIsZero = 0; 
    for i=startIdx:length(edgeArr)
        if (abs(edgeArr(i)) == edge) % this is an edge
            j = 1;
            while (abs(edgeArr(i+j)) ~= edge) && ((i+j) < length(edgeArr))
                j = j+1; % iterate until next edge
            end

            if ((j >= floor(0.45*tagPeriod)) && (j <= ceil(0.55*tagPeriod))) % zero
                if (prevIsZero == 0) % new half period, must be a zero
                    bitstream = [bitstream '0'];
                    prevIsZero = 1;
                else % previous bit is zero, this must be the other half period
                    prevIsZero = 0; % ignore this other half period
                end
            elseif ((j > floor(0.55*tagPeriod)) && (j <= ceil(1.4*tagPeriod)))
                bitstream = [bitstream '1'];
                prevIsZero = 0;
            elseif ((j > floor(1.4*tagPeriod)) && (j <= ceil(15*tagPeriod))) % 1.5*period means a v
                bitstream = [bitstream 'v'];
                prevIsZero = 0;
            else
                lastIdx = i;
                break; % end of response/backscatter from tag
            end
        end
    end
    
    % Set edge data before startIdx and after lastIdx to zero
    edgeArr(1:startIdx-1) = 0;
    edgeArr(lastIdx+1:end) = 0;
    hold on;
    plot (edgeArr)
end
