
function trialStruct = runSummary(taskStruct, dispStruct, trialStruct)
        
    % clear the screen for 1 second
    
    tSummaryStart = Screen(dispStruct.wPtr, 'Flip');

    Screen('TextSize', dispStruct.wPtr, 40);
    Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
    [~, ny] = DrawFormattedText(dispStruct.wPtr, '- Summary -', 'center', 50);
    
    Screen('TextSize', dispStruct.wPtr, 30);
    
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
    totalText = ['Total\n' num2str(trialStruct.totalEarnings) ' points'];
    [~, ny] = DrawFormattedText(dispStruct.wPtr, totalText, 'center', 'center', [], [], [], [], [], [], rectTotalLabel);
    
    text1 = 'Press any key to continue';
    Screen('TextSize', dispStruct.wPtr, 20);
    DrawFormattedText(dispStruct.wPtr, text1, 'center', ny + 80);
    
    % show summary
    [~, trialStruct.tSummaryOnset] = Screen(dispStruct.wPtr, 'Flip', tSummaryStart+1);
    
    % wait for key press to continue
    RestrictKeysForKbCheck( [] );
    KbWait(-3, 2);
    [~, trialStruct.tSummaryOffset] = Screen(dispStruct.wPtr, 'Flip');
    
end % run summary