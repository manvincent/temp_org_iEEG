% Got to directory where behavioural data are
homeDir = '/export/home/vman/iowa/behav/'
datDir = [homeDir];
% Define list of subjects to process
subList = {'567','585'};
blockLabels = {{'044','046'},{'060','063'}};

for s=1:length(subList)
    subID = subList{s};
    % Get the number of blocks
    blockList = {dir([datDir subID '*.mat']).name};
    % Iterate over blocks
    for b=1:length(blockList)
        % Load in data
        blockDat = load([datDir blockList{b}]);
        % Create table
        dataTable = struct2table(blockDat.taskStruct.allTrials);
        % Add first/second card IDs 
        dataTable = removevars(dataTable,{'cards'});
        cards_1 = blockDat.taskStruct.cardPairs(1:height(dataTable),1);
        cards_2 = blockDat.taskStruct.cardPairs(1:height(dataTable),2);        
        dataTable = addvars(dataTable,cards_2,'Before',1);
        dataTable = addvars(dataTable,cards_1,'Before',1);        
        dataTable.isTest = ones(height(dataTable),1);
        % Add regressors
        blockDat.taskStruct = buildRegressors(blockDat.taskStruct);
        dataTable.p1 = blockDat.taskStruct.p1;
        dataTable.peP1 = blockDat.taskStruct.peP1;
        dataTable.riskP1 = repmat(blockDat.taskStruct.riskP1,height(dataTable),1);
        dataTable.peRiskP1 =  blockDat.taskStruct.peRiskP1;
        dataTable.p2 =  blockDat.taskStruct.p2;
        dataTable.riskP2 =  blockDat.taskStruct.riskP2;
        dataTable.peP2 =  blockDat.taskStruct.peP2;
        dataTable.peRiskP2 =  blockDat.taskStruct.peRiskP2;
        % Output to csv 
        writetable(dataTable,[datDir 'patient' subID '_block' blockLabels{s}{b} '_behav.csv'])
    end   
end

