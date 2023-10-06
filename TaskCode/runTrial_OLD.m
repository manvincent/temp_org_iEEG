function trialStruct = runTrial_OLD(taskStruct, dispStruct, trialStruct)

    % randomize higher/lower buttons across left/right presentation
    buttonChoiceOrder = randperm(2);
    if buttonChoiceOrder(1) == taskStruct.HIGH
        buttonChoiceL = dispStruct.imgGuess_Higher;
        buttonChoiceR = dispStruct.imgGuess_Lower;
        trialStruct.choiceL = taskStruct.HIGH;
        trialStruct.choiceR = taskStruct.LOW;
    else
        buttonChoiceR = dispStruct.imgGuess_Higher;
        buttonChoiceL = dispStruct.imgGuess_Lower;
        trialStruct.choiceR = taskStruct.HIGH;
        trialStruct.choiceL = taskStruct.LOW;
    end
    
    % show the high/low choice buttons & wait for response
    Screen('DrawTexture', dispStruct.wPtr, buttonChoiceL, [], dispStruct.rectButton_Left);
    Screen('DrawTexture', dispStruct.wPtr, buttonChoiceR, [], dispStruct.rectButton_Right);
    
    % restrict keys, wait for keys to be lifted, then show the stimuli
    RestrictKeysForKbCheck( dispStruct.respKeyCodes );
    KbWait(-3, 1);
    [~, trialStruct.tGuessOnset] = Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response, and track response time
    [trialStruct.tGuessResp, keyCode, ~] = KbWait(-3, 2, GetSecs()+taskStruct.MAX_RT);
    trialStruct.rt_Guess = trialStruct.tGuessResp - trialStruct.tGuessOnset;
    
    % which response was made
    if ismember(find(keyCode, 1),dispStruct.respKey_Right )
        % store
        trialStruct.respKey_Guess = dispStruct.respRightID;
        trialStruct.resp_Guess = trialStruct.choiceR;
        % store button press location
        frameRect = dispStruct.rectButton_Right;
    elseif ismember(find(keyCode, 1),dispStruct.respKey_Left )
        % store left key press
        trialStruct.respKey_Guess = dispStruct.respLeftID;
        trialStruct.resp_Guess = trialStruct.choiceL;
        % store button press location
        frameRect = dispStruct.rectButton_Left;
    end
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], frameRect, 5);
    [~, trialStruct.tGuessFrameOnset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % clear the screen
    [~, trialStruct.tGuessOffset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % show the first card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(trialStruct.cards(1)), [], dispStruct.rectCard);
    [~, trialStruct.tCard1Onset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % clear card 1
    [~, trialStruct.tCard1Offset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % show the second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(trialStruct.cards(2)), [], dispStruct.rectCard);
    [~, trialStruct.tCard2Onset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % clear card 2
    [~, trialStruct.tCard2Offset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % outcome confirmation 
    
    % randomize win/loss buttons across left/right
    buttonConfirmOrder = randperm(2);
    if buttonConfirmOrder(1) == taskStruct.WIN
        buttonReport_Left = dispStruct.imgReport_Win;
        buttonReport_Right = dispStruct.imgReport_Loss;
        trialStruct.report_Left = taskStruct.WIN;
        trialStruct.report_Right = taskStruct.LOSS;
        
    else
        buttonReport_Right = dispStruct.imgReport_Win;
        buttonReport_Left = dispStruct.imgReport_Loss;
        trialStruct.report_Right = taskStruct.WIN;
        trialStruct.report_Left = taskStruct.LOSS;
    end
    
    % show win/loss buttons
    Screen('DrawTexture', dispStruct.wPtr, buttonReport_Left, [], dispStruct.rectButton_Left);
    Screen('DrawTexture', dispStruct.wPtr, buttonReport_Right, [], dispStruct.rectButton_Right);
    
    % restrict keys, wait for keys to be lifted, then show the stimuli
    RestrictKeysForKbCheck( dispStruct.respKeyCodes );
    KbWait(-3, 1);
    RestrictKeysForKbCheck( [] );
    [~, trialStruct.tReportOnset] = Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % wait for response, and track response time
    [trialStruct.tReportResp, keyCode, ~] = KbWait(-3, 2, GetSecs()+taskStruct.MAX_RT);
    trialStruct.rt_Report = trialStruct.tReportResp - trialStruct.tReportOnset;
    
    % which response was made
    if ismember(find(keyCode, 1),dispStruct.respKey_Right )
        % right key
        trialStruct.respKey_Report = dispStruct.respRightID;
        trialStruct.resp_Report = trialStruct.report_Right;
        % store button press location
        frameRect = dispStruct.rectButton_Right;
    elseif ismember(find(keyCode, 1),dispStruct.respKey_Left )
        trialStruct.respKey_Report = dispStruct.respLeftID;
        trialStruct.resp_Report = trialStruct.report_Left;
        % store button press location
        frameRect = dispStruct.rectButton_Left;
    end
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], frameRect, 5);
    [~, trialStruct.tConfirmFrameOnset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    % clear the screen
    [~, trialStruct.tConfirmOffset] = Screen(dispStruct.wPtr, 'Flip');
    WaitSecs(1);
    
    %%%%%%%%%%%%%%%%%%%%%%55
    % Outcome
    
    % did they guess card ordering correctly?
    trialStruct.isCorrectChoice = (trialStruct.isHigher && trialStruct.resp_Guess == taskStruct.HIGH) || (~trialStruct.isHigher && trialStruct.resp_Guess == taskStruct.LOW);
    % determin the guess earnings
    if trialStruct.isCorrectChoice
        trialStruct.guessEarnings = taskStruct.GUESS_WIN_AMOUNT;
    else
        trialStruct.guessEarnings = taskStruct.GUESS_LOSS_AMOUNT;
    end
    
    % did the confirmation match what actually happened?
    trialStruct.isCorrectConfirm = (trialStruct.resp_Report == taskStruct.WIN && trialStruct.isCorrectChoice) || (trialStruct.resp_Report == taskStruct.LOSS && ~trialStruct.isCorrectChoice);
    % did they match their earnings
    if trialStruct.isCorrectConfirm
        trialStruct.reportEarnings = taskStruct.CLAIM_MATCH_WIN;
    else
        trialStruct.reportEarnings = taskStruct.CLAIM_MATCH_LOSS;
    end
    
    runSummary(taskStruct, dispStruct, trialStruct);
    
    % clear the screen
    trialStruct.tTrialEnd = GetSecs();
    
end % run trial

function [] = runSummary(taskStruct, dispStruct, trialStruct)
    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, [0 0 0]);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '- Instructions 1 -', 'center', 25);
    
    Screen('TextSize', dispStruct.wPtr, 30);
    Screen('TextColor', dispStruct.wPtr, [0 0 0]);
    
    % guess feedback
    guessLabel = 'Guess';
    if trialStruct.resp_Guess == taskStruct.HIGH
        guessButton = dispStruct.imgGuess_Higher;
    else
        guessButton = dispStruct.imgGuess_Lower;
    end
    guessText = [num2str(trialStruct.guessEarnings) ' points'];
    % Guess feedback locations
    leftX = dispStruct.centerX - (dispStruct.buttonWidth/2);
    topY = ny + 100;
    rectGuessLabel = [leftX, topY, leftX+dispStruct.buttonWidth, topY+20];
    topY = rectGuessLabel(4) + 10;
    rectGuessButton = dispStruct.rectButton + [leftX, topY, leftX, topY];
    topY = rectGuessButton(4) + 10;
    rectGuessPoints = [leftX, topY, leftX+dispStruct.buttonWidth, topY+20];
    % draw guess info to screen
    DrawFormattedText(dispStruct.wPtr, guessLabel, 'center', 'center', [], [], [], [], [], [], rectGuessLabel);
    Screen('DrawTexture', dispStruct.wPtr, guessButton, [], rectGuessButton);
    DrawFormattedText(dispStruct.wPtr, guessText, 'center', 'center', [], [], [], [], [], [], rectGuessPoints);
    
    
    % report
    reportLabel = 'Report';
    if trialStruct.resp_Report == taskStruct.WIN
        reportButton = dispStruct.imgReport_Win;
    else
        reportButton = dispStruct.imgReport_Loss;
    end
    reportText = [num2str(trialStruct.reportEarnings) ' points'];
    % Guess feedback locations
    leftX = dispStruct.centerX - (dispStruct.buttonWidth/2);
    topY = rectGuessPoints(4) + 50;
    rectReportLabel = [leftX, topY, leftX+dispStruct.buttonWidth, topY+20];
    topY = rectReportLabel(4) + 10;
    rectReportButton = dispStruct.rectButton + [leftX, topY, leftX, topY];
    topY = rectReportButton(4) + 10;
    rectReportPoints = [leftX, topY, leftX+dispStruct.buttonWidth, topY+20];
    % draw guess info to screen
    DrawFormattedText(dispStruct.wPtr, reportLabel, 'center', 'center', [], [], [], [], [], [], rectReportLabel);
    Screen('DrawTexture', dispStruct.wPtr, reportButton, [], rectReportButton);
    DrawFormattedText(dispStruct.wPtr, reportText, 'center', 'center', [], [], [], [], [], [], rectReportPoints);
    
    % total
    leftX = dispStruct.centerX - (dispStruct.buttonWidth/2);
    topY = rectReportPoints(4) + 75;
    rectTotalLabel = [leftX, topY, leftX+dispStruct.buttonWidth, topY+40];
    totalText = ['Total\n' num2str(trialStruct.guessEarnings+trialStruct.reportEarnings) ' points'];
    [~, ny] = DrawFormattedText(dispStruct.wPtr, totalText, 'center', 'center', [], [], [], [], [], [], rectTotalLabel);
    
    text1 = 'Press any key to continue';
    Screen('TextSize', dispStruct.wPtr, 20);
    DrawFormattedText(dispStruct.wPtr, text1, 'center', ny + 80);
    
    % show summary
    [~, trialStruct.tGuessOutcomeOnset] = Screen(dispStruct.wPtr, 'Flip');
    
    % wait for key press to continue
    RestrictKeysForKbCheck( [] );
    KbWait(-3, 2);
    Screen(dispStruct.wPtr, 'Flip');
    
end % run summary
