

%initialize
[taskStruct, dispStruct] = initTask();
taskStruct.expStartTime = GetSecs();
taskStruct.totalEarnings = 0;
taskStruct.trialTotal = 0;

% note experiment start time
fireEvent(taskStruct.LPT, taskStruct.eEXP_START);

try
    % run the instructiona
    %runCardDrawInstructions(taskStruct, dispStruct);

    % run a few practice trials
    [taskStruct, dispStruct] = runPractice(taskStruct, dispStruct);
    
    % fire test start event
    fireEvent(taskStruct.LPT, taskStruct.eTEST_START);

    % run through each trial
    for tI = 1 : size(taskStruct.cardPairs,1)
        % build this trial's structure
        trialStruct = buildTrialStruct(taskStruct.cardPairs(tI, :));
        taskStruct.trialTotal = taskStruct.trialTotal + 1;

        % create a new struct on trial 1, compile thereafter
        if tI == 1
            taskStruct.allTrials = runTrial(taskStruct, dispStruct, trialStruct);
        else
            taskStruct.allTrials(tI) = runTrial(taskStruct, dispStruct, trialStruct);
        end

%         % show the summary screen if a valid response was made
%         if taskStruct.allTrials(tI).resp_Guess ~= taskStruct.SLOW && taskStruct.allTrials(tI).resp_Report ~= taskStruct.SLOW
%             taskStruct.allTrials(tI) = runSummary(taskStruct, dispStruct, taskStruct.allTrials(tI));
%         end
    
        % sum total earnings
        taskStruct.totalEarnings = taskStruct.totalEarnings + taskStruct.allTrials(tI).totalEarnings;
        
        % save the data
        save( fullfile(taskStruct.outputFolder, taskStruct.fileName));
        
        % should we show a break
        if mod(tI, taskStruct.BREAK_BLOCK) == 0 && tI < size(taskStruct.cardPairs,1)
            runBreak(taskStruct, dispStruct);
        end
        
        
        % check for quit button
        RestrictKeysForKbCheck( [dispStruct.respKey_Quit, dispStruct.respKey_Pause] );
        [secs, keyCode] = KbWait( -3, 0, GetSecs()+0.10);
        if ismember(find(keyCode, 1),dispStruct.respKey_Quit )
            RestrictKeysForKbCheck( [] );
            Screen('TextSize', dispStruct.wPtr, 30);
            Screen('TextColor', dispStruct.wPtr, dispStruct.textColor);
            text1 = 'Do you really want to quit?\n\n';
            [~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', 'center');
            Screen(dispStruct.wPtr, 'Flip');

            % wait for a second Q press (or any other key to continue) 
            [secs, keyCode] = KbWait( -3, 2);
            if ismember(find(keyCode, 1),dispStruct.respKey_Quit )
                % terminate
                throw(MException(-1, 'user quit'));
            end
        elseif ismember(find(keyCode, 1),dispStruct.respKey_Pause )
            runPause(taskStruct, dispStruct);
        end
        
    end % for each card pair
    
    % fire test start event
    fireEvent(taskStruct.LPT, taskStruct.eTEST_END);

catch ME
    % carry on to the final screen
    fireEvent(taskStruct.LPT, taskStruct.eTEST_ABORT);
end


% instruction text
% taskStruct.totalEarnings = nansum(cell2mat({taskStruct.allTrials(:).guessEarnings})) + nansum(cell2mat({taskStruct.allTrials(:).reportEarnings}));
Screen('TextSize', dispStruct.wPtr, 30);
text1 = 'You''re done!\n\nThank you for participating today.\n\n';
text2 = ['You earned a total of ' num2str(taskStruct.totalEarnings) ' points.'];

[~, ny] = DrawFormattedText(dispStruct.wPtr, text1, 'center', dispStruct.centerY - 30, [], 70, false, false, 1.1);
[~, ny] = DrawFormattedText(dispStruct.wPtr, text2, 'center', ny, [], 70, false, false, 1.1);
Screen(dispStruct.wPtr, 'Flip');

% capture completion time
taskStruct.expDoneTime = GetSecs();
% save the data
save( fullfile(taskStruct.outputFolder, taskStruct.fileName));

% wait for key press to continue
RestrictKeysForKbCheck( KbName('space') );
KbWait(-3, 2);

% fire end of experiment
fireEvent(taskStruct.LPT, taskStruct.eEXP_END);

% clean things up
ListenChar(0);
RestrictKeysForKbCheck( [] );
ShowCursor();
sca;


