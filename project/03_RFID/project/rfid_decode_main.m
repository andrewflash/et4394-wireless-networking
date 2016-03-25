% Main Function - Decode RFID Raw data
% -- Andri Rahmadhani & Bontor Humala, March 2016

% Set parameters
fName = 'signal.txt';
window = 2;
curIdx = 1;     % Current index, pointer to data

% Read RFID raw data from file
fHandle = fopen(fName);
formatData = '%f';
rawData = fscanf(fHandle, formatData);
fclose(fHandle);

% Filter moving average
mvAvgArr = [];
for i=1:length(rawData)-window
    mvAvg = 0;    
    for j=i:(i+window)
        mvAvg = mvAvg + rawData(j);
    end
    mvAvg = mvAvg/window;
    mvAvgArr = [mvAvgArr mvAvg];
end

figure(1);
%plot(rawData);
%hold on;
plot (mvAvgArr);

% Read first query from reader
stdThres = 0.5;
stdWindow = 10;
[bitstreamReader, lastIdx] = readReader(mvAvgArr, curIdx, stdThres, stdWindow); 
curIdx = lastIdx+1;

% Read first tag data
stdThres = 0.2;     % 
stdWindow = 5;
[bitstreamTag, lastIdx] = readTag(mvAvgArr, curIdx, stdThres, stdWindow); 
curIdx = lastIdx+1;

% Read second query from reader
stdThres = 0.5;
stdWindow = 10;
[bitstreamReader2, lastIdx] = readReader(mvAvgArr, curIdx, stdThres, stdWindow); 
curIdx = lastIdx+1;

% Read second tag data
stdThres = 0.2;
stdWindow = 5;
[bitstreamTag2, lastIdx] = readTag(mvAvgArr, curIdx, stdThres, stdWindow); 
curIdx = lastIdx+1;
