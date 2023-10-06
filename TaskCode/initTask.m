function [taskStruct, dispStruct] = initTask()
    % some initial global setup
    RandStream.setGlobalStream(RandStream('mt19937ar','Seed','shuffle'));
    KbName('UnifyKeyNames');
    RestrictKeysForKbCheck( [] );
%     Screen('Preference', 'SkipSyncTests', 1);
    
    % general task info
    taskStruct = struct();
    
    % initialize the trigger port
    %taskStruct.LPT = initializeLPT;
    taskStruct.LPT = struct([]);
    
    % define event codes
    taskStruct.eEXP_START = 1;
    taskStruct.eEXP_END = 2;
    taskStruct.ePRACTICE_START = 3;
    taskStruct.ePRACTICE_END = 4;
    taskStruct.eTEST_START = 5;
    taskStruct.eTEST_END = 6;
    taskStruct.eTEST_ABORT = 7;
    
    taskStruct.eTRIAL_START = 8;
    taskStruct.eGUESS_ON = 9;
    taskStruct.eGUESS_RESP = 10;
    taskStruct.eCARD1_ON = 11;
    taskStruct.eCARD1_OFF = 12;
    taskStruct.eCARD2_ON = 13;
    taskStruct.eREPORT_ON = 14;
    taskStruct.eREPORT_RESP = 15;
    taskStruct.eTRIAL_END = 16;
    
    
    % subejct ID info
    taskStruct.subID = input('Participant number :\n','s');
    % output folder
    taskStruct.outputFolder = fullfile('..', 'data');
    % check to see if the output folder exists
    if exist(taskStruct.outputFolder, 'dir') == 0
        % folder does not exist - create it
        mkdir( taskStruct.outputFolder );
    end
    taskStruct.fileName = [taskStruct.subID '_Sub_Amb_' datestr(now, 'mm-dd-yyyy_HH-MM-SS')];
    
    % response options
    taskStruct.HIGH = 1;
    taskStruct.LOW = 2;
    taskStruct.WIN = 1;
    taskStruct.LOSS = 2;
    taskStruct.GUESS_WIN_AMOUNT = 10;
    taskStruct.GUESS_LOSS_AMOUNT = -10;
    taskStruct.CLAIM_MATCH_WIN = 5;
    taskStruct.CLAIM_MATCH_LOSS = -5;
    taskStruct.SLOW_AMOUNT = -10;
    
    taskStruct.MAX_RT = 7;
    taskStruct.BREAK_BLOCK = 5;
    taskStruct.SLOW = -1;
    
    % define the card orderings for each trial
    taskStruct.cardPairs = [combnk(1:10,2); fliplr(combnk(1:10,2))];
    % randomize the order
    cardOrder = randperm(size(taskStruct.cardPairs, 1));
    taskStruct.cardPairs = taskStruct.cardPairs(cardOrder, :);
    
    
    
    % set up the screen
    dispStruct = struct();
    dispStruct.bgColor = [60 60 60];
    dispStruct.textColor = [200 200 200];
    screenDebug = [0,0,1000,800]; % screen for debugging
    screenTask = []; % full screen
    [dispStruct.wPtr, dispStruct.wPtrRect] = Screen('OpenWindow', 0, dispStruct.bgColor, screenDebug);
    % Measure the vertical refresh rate of the monitor
    dispStruct.ifi = Screen('GetFlipInterval', dispStruct.wPtr);
    dispStruct.centerX = round(dispStruct.wPtrRect(3)/2);
    dispStruct.centerY = round(dispStruct.wPtrRect(4)/2);
%     Screen('TextFont', dispStruct.wPtr, 'Helvetica');

    
    % response keys
    dispStruct.respKey_Right = [ KbName('3#'), KbName('3') ];
    dispStruct.respKeyName_Right = 'R';
    dispStruct.respKey_Left = [ KbName('1!'), KbName('1') ];
    dispStruct.respKeyName_Left = 'L';
    dispStruct.respKey_Quit = KbName('Q');
    dispStruct.respKeyName_Quit = 'Q';
    dispStruct.respKey_Pause = KbName('P');
    dispStruct.respKeyName_Pause = 'P';
    
    % stimuli are drawn from left to right, so index left as 1
    dispStruct.respLeftID = 1;
    dispStruct.respRightID = 2;
    dispStruct.respKeyCodes = [dispStruct.respKey_Left, dispStruct.respKey_Right];
    dispStruct.kbCheckPause = 0.0005;
    
    % the card rect
    scallingFactor = 2;
    rectCard_width = scallingFactor*73; rectCard_height = scallingFactor*100;
    rectCard_LeftX = dispStruct.centerX - (rectCard_width/2);
    rectCard_TopY = dispStruct.centerY - (rectCard_height/2);
    dispStruct.rectCard = [rectCard_LeftX, rectCard_TopY, rectCard_LeftX+rectCard_width, rectCard_TopY+rectCard_height];
    
    % define choice rects
    dispStruct.buttonWidth = 150;
    dispStruct.buttonHeight = 100;
    dispStruct.rectButton = [0 0 dispStruct.buttonWidth dispStruct.buttonHeight];
    rectChoice_gap = rectCard_width + 50;
    % put left/right choices into position
    rectButton_LeftX = dispStruct.centerX - (rectChoice_gap/2) - dispStruct.buttonWidth;
    rectButton_TopY = dispStruct.centerY - (dispStruct.buttonHeight/2);
    dispStruct.rectButtonGuess_Left = dispStruct.rectButton + [rectButton_LeftX, rectButton_TopY, rectButton_LeftX, rectButton_TopY];
    % right choice
    rectButton_LeftX = dispStruct.centerX + (rectChoice_gap/2);
    rectButton_TopY = dispStruct.centerY - (dispStruct.buttonHeight/2);
    dispStruct.rectButtonGuess_Right = dispStruct.rectButton + [rectButton_LeftX, rectButton_TopY, rectButton_LeftX, rectButton_TopY];
    
    % report buttons
    dispStruct.buttonReportWidth = 130;
    dispStruct.buttonReportHeight = 80;
    dispStruct.rectButton = [0 0 dispStruct.buttonWidth dispStruct.buttonHeight];
    rectChoice_gap = 100;
    % put left/right reports into position
    rectButton_LeftX = dispStruct.centerX - (rectChoice_gap/2) - dispStruct.buttonWidth;
    rectButton_TopY = dispStruct.rectCard(4) + 100;
    dispStruct.rectButtonReport_Left = dispStruct.rectButton + [rectButton_LeftX, rectButton_TopY, rectButton_LeftX, rectButton_TopY];
    % right choice
    rectButton_LeftX = dispStruct.centerX + (rectChoice_gap/2);
    dispStruct.rectButtonReport_Right = dispStruct.rectButton + [rectButton_LeftX, rectButton_TopY, rectButton_LeftX, rectButton_TopY];
    
    
    % load choice and feedback images
    dispStruct.imgGuess_Lower = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', 'button_Lower.png')));
    dispStruct.imgGuess_Higher = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', 'button_Higher.png')));
    % confirmation
    dispStruct.imgReport_Win = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', 'button_Win.png')));
    dispStruct.imgReport_Loss = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', 'button_Loss.png')));
    
    % load the card images
    dispStruct.imgCards = nan(10,1);
    for cI = 1 : length(dispStruct.imgCards)
        dispStruct.imgCards(cI) = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', [num2str(cI) '.png'])));
    end
    
    % load in the leader board
    dispStruct.leaderBoard = Screen('MakeTexture', dispStruct.wPtr, imread(fullfile('Images', 'LeaderBoard.png')));
    
    
    ListenChar(2);
    HideCursor();
end