function trialStruct = buildTrialStruct(cards)
    trialStruct = struct();
    trialStruct.cards = cards;
    trialStruct.isHigher = trialStruct.cards(1) < trialStruct.cards(2);
    % choice left/right
    trialStruct.guessL = NaN;
    trialStruct.guessR = NaN;
    % actual choice
    trialStruct.respKey_Guess = NaN;
    trialStruct.resp_Guess = NaN;
    % report left/right
    trialStruct.reportL = NaN;
    trialStruct.reportR = NaN;
    trialStruct.respKey_Report = NaN;
    trialStruct.resp_Report = NaN;
    
    % response times
    trialStruct.rt_Guess = NaN;
    trialStruct.rt_Report = NaN;
    
    % accuracy
    trialStruct.isCorrectGuess = NaN;
    trialStruct.isCorrectReport = NaN;
    
    % points earned
    trialStruct.totalEarnings = NaN;
    trialStruct.guessEarnings = NaN;
    trialStruct.reportEarnings = NaN;
    
    % event times
    trialStruct.tTrialStart = NaN;
    trialStruct.tGuessOnset = NaN;
    trialStruct.tGuessResp = NaN;
    trialStruct.tCard1Fixation = NaN;
    trialStruct.tCard1Onset = NaN;
    trialStruct.tCard1Offset = NaN;
    trialStruct.tCard2Fixation = NaN;
    trialStruct.tCard2Onset = NaN;
    trialStruct.tCard2Offset = NaN;
    trialStruct.tReportOnset = NaN;
    trialStruct.tReportResp = NaN;
    trialStruct.tReportFrameOnset = NaN;
    trialStruct.tReportOffset = NaN;
    trialStruct.tTrialEnd = NaN;
    trialStruct.tSummaryOnset = NaN;
    trialStruct.tSummaryOffset = NaN;
end
