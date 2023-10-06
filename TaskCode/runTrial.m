function trialStruct = runTrial(taskStruct, dispStruct, trialStruct)

    % clear the screen for 1 second
    trialStruct.tTrialStart = Screen(dispStruct.wPtr, 'Flip');
    fireEvent(taskStruct.LPT, taskStruct.eTRIAL_START);
    

    % randomize higher/lower buttons across left/right presentation
    buttonChoiceOrder = randperm(2);
    if buttonChoiceOrder(1) == taskStruct.HIGH
        buttonChoiceL = dispStruct.imgGuess_Higher;
        buttonChoiceR = dispStruct.imgGuess_Lower;
        trialStruct.guessL = taskStruct.HIGH;
        trialStruct.guessR = taskStruct.LOW;
    else
        buttonChoiceR = dispStruct.imgGuess_Higher;
        buttonChoiceL = dispStruct.imgGuess_Lower;
        trialStruct.guessR = taskStruct.HIGH;
        trialStruct.guessL = taskStruct.LOW;
    end
    
    % show the high/low choice buttons & wait for response
    Screen('DrawTexture', dispStruct.wPtr, buttonChoiceL, [], dispStruct.rectButtonGuess_Left);
    Screen('DrawTexture', dispStruct.wPtr, buttonChoiceR, [], dispStruct.rectButtonGuess_Right);
    
    % restrict keys, wait for keys to be lifted, then show the stimuli
    KbWait(-3, 1);
    RestrictKeysForKbCheck( dispStruct.respKeyCodes );
    trialStruct.tGuessOnset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tTrialStart+1, 1);
    fireEvent(taskStruct.LPT, taskStruct.eGUESS_ON);
    
    % start polling for a key press
    waitForGuess = true;
    tKBEndWait = GetSecs()+taskStruct.MAX_RT;
    while GetSecs < tKBEndWait && waitForGuess
        % check the keys
        [keyIsDown,trialStruct.tGuessResp,keyCode] = KbCheck(-3);
        if keyIsDown
            waitForGuess = false;
        end
        WaitSecs(dispStruct.kbCheckPause);
    end
    % compute RT
    trialStruct.rt_Guess = trialStruct.tGuessResp - trialStruct.tGuessOnset;
    fireEvent(taskStruct.LPT, taskStruct.eGUESS_RESP);
    
    % which response was made
    if ismember(find(keyCode, 1),dispStruct.respKey_Right )
        % store
        trialStruct.respKey_Guess = dispStruct.respRightID;
        trialStruct.resp_Guess = trialStruct.guessR;
        % store button press location
        rejectRect = dispStruct.rectButtonGuess_Left;
    elseif ismember(find(keyCode, 1),dispStruct.respKey_Left )
        % store left key press
        trialStruct.respKey_Guess = dispStruct.respLeftID;
        trialStruct.resp_Guess = trialStruct.guessL;
        % store button press location
        rejectRect = dispStruct.rectButtonGuess_Right;
    else
        % no response made in time
        trialStruct.resp_Guess = taskStruct.SLOW;
        trialStruct.totalEarnings = taskStruct.SLOW_AMOUNT;
        
        % show slow penalty screen and exit
        runTooSlow(taskStruct, dispStruct, trialStruct);
        return;
    end
    
    % Hide the rejected option & show fixation
    Screen('FillRect', dispStruct.wPtr, dispStruct.bgColor, rejectRect);    
    tButtonHide = Screen(dispStruct.wPtr, 'Flip', 0, 1);
    
    % show fixation
    Screen('TextSize', dispStruct.wPtr, 45);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    trialStruct.tCard1Fixation = Screen(dispStruct.wPtr, 'Flip', tButtonHide+1, 1);
    
    % show the first card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(trialStruct.cards(1)), [], dispStruct.rectCard);
    trialStruct.tCard1Onset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tCard1Fixation+1.5, 1);
    fireEvent(taskStruct.LPT, taskStruct.eCARD1_ON);
    
    % clear card 1 & show fixation
    Screen('FillRect', dispStruct.wPtr, dispStruct.bgColor, dispStruct.rectCard);
    Screen('TextSize', dispStruct.wPtr, 45);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    DrawFormattedText(dispStruct.wPtr, '+', 'center', 'center', [], 70, false, false, 1.1);
    trialStruct.tCard1Offset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tCard1Onset+2, 1);
    fireEvent(taskStruct.LPT, taskStruct.eCARD1_OFF);
    
    % show the second card
    Screen('DrawTexture', dispStruct.wPtr, dispStruct.imgCards(trialStruct.cards(2)), [], dispStruct.rectCard);
    trialStruct.tCard2Onset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tCard1Offset+1.5, 1);
    fireEvent(taskStruct.LPT, taskStruct.eCARD2_ON);
    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % outcome confirmation 
    
    % randomize win/loss buttons across left/right
    buttonConfirmOrder = randperm(2);
    if buttonConfirmOrder(1) == taskStruct.WIN
        buttonReport_Left = dispStruct.imgReport_Win;
        buttonReport_Right = dispStruct.imgReport_Loss;
        trialStruct.reportL = taskStruct.WIN;
        trialStruct.reportR = taskStruct.LOSS;
        
    else
        buttonReport_Right = dispStruct.imgReport_Win;
        buttonReport_Left = dispStruct.imgReport_Loss;
        trialStruct.reportR = taskStruct.WIN;
        trialStruct.reportL = taskStruct.LOSS;
    end
    
    % show win/loss buttons
    Screen('DrawTexture', dispStruct.wPtr, buttonReport_Left, [], dispStruct.rectButtonReport_Left);
    Screen('DrawTexture', dispStruct.wPtr, buttonReport_Right, [], dispStruct.rectButtonReport_Right);
    
    % restrict keys, wait for keys to be lifted, then show the stimuli
    KbWait(-3, 1);
    RestrictKeysForKbCheck( dispStruct.respKeyCodes );
    trialStruct.tReportOnset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tCard2Onset+2, 1);
    fireEvent(taskStruct.LPT, taskStruct.eREPORT_ON);
    
    % wait for response, and track response time
    waitForReport = true;
    tKBEndWait = GetSecs()+taskStruct.MAX_RT;
    while GetSecs < tKBEndWait && waitForReport
        % check the keys
        [keyIsDown,trialStruct.tReportResp,keyCode] = KbCheck(-3);
        if keyIsDown
            waitForReport = false;
        end
        WaitSecs(dispStruct.kbCheckPause);
    end
    trialStruct.rt_Report = trialStruct.tReportResp - trialStruct.tReportOnset;
    fireEvent(taskStruct.LPT, taskStruct.eREPORT_RESP);
    
    % which response was made
    if ismember(find(keyCode, 1),dispStruct.respKey_Right )
        % right key
        trialStruct.respKey_Report = dispStruct.respRightID;
        trialStruct.resp_Report = trialStruct.reportR;
        % store button press location
        frameRect = dispStruct.rectButtonReport_Right;
    elseif ismember(find(keyCode, 1),dispStruct.respKey_Left )
        trialStruct.respKey_Report = dispStruct.respLeftID;
        trialStruct.resp_Report = trialStruct.reportL;
        % store button press location
        frameRect = dispStruct.rectButtonReport_Left;    
    else
        % no response made in time
        trialStruct.resp_Report = taskStruct.SLOW;
        trialStruct.totalEarnings = taskStruct.SLOW_AMOUNT;
        
        % show slow penalty screen and exit
        runTooSlow(taskStruct, dispStruct, trialStruct);
        return;
        
    end
    
    % frame the choice
    Screen('FrameRect', dispStruct.wPtr, [0 0 255], frameRect, 5);
    [~, trialStruct.tReportFrameOnset] = Screen(dispStruct.wPtr, 'Flip');
    % clear the screen
    trialStruct.tReportOffset = Screen(dispStruct.wPtr, 'Flip', trialStruct.tReportFrameOnset+1);
    
    %%%%%%%%%%%%%%%%%%%%%%55
    % Outcome
    
    % did they guess card ordering correctly?
    trialStruct.isCorrectGuess = (trialStruct.isHigher && trialStruct.resp_Guess == taskStruct.HIGH) || (~trialStruct.isHigher && trialStruct.resp_Guess == taskStruct.LOW);
    % determin the guess earnings
    if trialStruct.isCorrectGuess
        trialStruct.guessEarnings = taskStruct.GUESS_WIN_AMOUNT;
    else
        trialStruct.guessEarnings = taskStruct.GUESS_LOSS_AMOUNT;
    end
    
    % did the confirmation match what actually happened?
    trialStruct.isCorrectReport = (trialStruct.resp_Report == taskStruct.WIN && trialStruct.isCorrectGuess) || (trialStruct.resp_Report == taskStruct.LOSS && ~trialStruct.isCorrectGuess);
    % did they match their earnings
    if trialStruct.isCorrectReport
        trialStruct.reportEarnings = taskStruct.CLAIM_MATCH_WIN;
    else
        trialStruct.reportEarnings = taskStruct.CLAIM_MATCH_LOSS;
    end
    
    % total earnings
    trialStruct.totalEarnings = trialStruct.guessEarnings + trialStruct.reportEarnings;
    
    % clear the screen
    trialStruct.tTrialEnd = GetSecs();
    
    fireEvent(taskStruct.LPT, taskStruct.eTRIAL_END);
    
end % run trial