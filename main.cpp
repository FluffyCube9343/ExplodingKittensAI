#include <iostream>
#include <unordered_map>
#include <string>
#include <cstdlib>
#include <ctime>
#include <numeric>
#include <algorithm>
#include <random>
#include <sstream>
#include <ctime>
#include <fstream>
#include <vector>
#include <chrono>

using namespace std;

mt19937 g(12);


int hit = 0;
int cache = 0;
long numberofstates = 0;
unordered_map<uint64_t, vector<pair<long,long>>> totalstates;
unordered_map<uint64_t, vector<pair<long,long>>> totalfavors;

/*
    Structure:
        Key: unsigned 64-int as encoded game state
        Value: 12-vector of (wins, totals)

*/



string vectorToString(const std::vector<int>& v) {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < v.size(); ++i) {
        oss << v[i];
        if (i + 1 < v.size()) oss << ", ";
    }
    oss << "]";
    return oss.str();
}


int weightedRandom(vector<int> weights, int total){
    int chosen = rand()%total;
    int runningsum = 0;
    // cout << "wR: "<< vectorToString(weights) << " " << total<< " " << chosen << "\n" ;
    
    for(int i=0;i<12;i++){
        runningsum += weights[i];
        if(runningsum > chosen){
            // cout << "RNG successful "<< i << "\n";
            return i;
        }
    }
    cout << "Something has gone wrong" << endl;
    return 12;
}

string getState(int toDraw, int lendeck, vector<int> deck, int deckhandlens){
    string r = "";
    r += to_string(toDraw);
    r += ",";
    r += lendeck;
    r += ",";
    for(int i=0;i<12;i++){
        r += to_string(deck[i]);
        r += ",";
    }
    r += to_string(deckhandlens);
    r += ",";
    return r;
}


int giveRandomMove(vector<int> deck, int name, int deckhandlens, int numPlayable, int lendeck, int toDraw){
    if(numPlayable ==0){
        return 0;
    }
    if(rand()%(numPlayable+1) == 0){
        return 0;
    }

    int victim = name^1;

    vector<int> possible(12);
    possible[2] = deck[2];
    possible[3] = deck[3];
    possible[5] = deck[5];
    possible[6] = deck[6];
    if(deckhandlens!=0){ //favor/catcard-able
        possible[4] = deck[4];
        possible[7] = deck[7]/2;
        possible[8] = deck[8]/2;
        possible[9] = deck[9]/2;
        possible[10] = deck[10]/2;
        possible[11] = deck[11]/2;
        
    }

    int total = accumulate(possible.begin(),possible.end(),0);
    if(total == 0){
        return 0;
    }

    uint64_t state = toDraw;
    state <<= 4;
    state |= lendeck;

    const auto &hand = deck;
    for (int i = 0; i < 12; i++) {
        state <<= 3;
        state |= hand[i];
    }

    state <<= 6;
    state |= deckhandlens;

    
    if(totalstates.find(state)!=totalstates.end()){
        // cout << "HIT\n";
        vector<pair<long,long>> vp = totalstates[state];
        for(int i=0;i<12;i++){
            if(possible[i]!=0 && vp[i].second==0){
                return i;
            }
        }
    }
    


    // string state = getState(toDraw,lendeck,deck,deckhandlens);
    // if(totalstates.count(state)==0){
    //     return weightedRandom(possible,total);
    // }
    // else{
    //     unordered_map traversed = totalstates[state];
    //     for(int i=0;i<12;i++){
    //         if(possible[i]!=0 && traversed.count(i)==0){
    //             return i;
    //         }
    //     }

    // cout << vectorToString(possible) << " " << vectorToString(deck) << "\n";
    return weightedRandom(possible,total);
    // }


}


pair<int,int> simulateGame2(int players, vector<int> unexposed, vector<int> yours, int lenDeck, int theirs, int toDraw, int turn, int opDefuse, vector<int> deckifgiven);


class Player{
    public:
        int name;
        int numPlayable;
        int numCards;
        vector<int> hand;
        vector<int> hidden;
        int opDefuse;
        // int decklen;

        Player(int n, vector<int> h, int dl){
            name = n;
            hand = h;
            numCards = accumulate(h.begin(),h.end(),0);
            hidden = {4, 5, 4, 4, 4, 4, 5, 4, 4, 4, 4, 4};
            numPlayable = hand[2]+hand[3]+hand[4]+hand[5]+hand[6]+hand[7]/2+hand[8]/2+hand[9]/2+hand[10]/2+hand[11]/2;
            for(int i=0;i<12;i++){
                hidden[i]-=hand[i];
            }
            opDefuse = 1;
            // decklen = dl;
        }
    
        void inform(int player, int move, int victim, int cardtaken){
            if(player!=name && move>=7 && victim==name){ //lose a card
                if(cardtaken>=2 && cardtaken<=6){
                    numPlayable-=1;
                }
                else if(cardtaken >= 7 and hand[cardtaken]%2==1){
                    numPlayable-=1;
                }
                if(cardtaken==0){
                    opDefuse += 1;
                }
                hidden[cardtaken] += 1;

            }
            else if(player!=name && move==4 && victim==name){//lose card via favor
                //favor logic done in game simulation
                hidden[cardtaken] += 1;
            }
            else if(player==name && (move==4 || move>=7)){ //gain a card
                if(cardtaken>=2 && cardtaken<=6){
                    numPlayable+=1;
                }
                else if(cardtaken >= 7 and hand[cardtaken]%2==0){
                    numPlayable+=1;
                }
                if(cardtaken==0){
                    opDefuse -= 1;
                    // if(opDefuse < 0){cout << "Negative! something went wrong lol \n"; cin.get();}
                }
                hidden[cardtaken] -= 1;
                if(hidden[cardtaken] < 0){cout << "Negative! something went wrong lol2 \n"; cin.get();}
            }
            if(player!=name and move > 0){
                hidden[move] -= 1;
                if(move >= 7){
                    hidden[move] -= 1;
                }
                if(hidden[move] < 0){cout << "Negative! something went wrong lol4 \n"; cin.get();}
            }
            if(player!=name and move == -1){
                hidden[0] -= 1;
                opDefuse -= 1;
            }
            if(move==0){
                // decklen -= 1;
                // if(decklen < 0){
                //     cout << "oopsies\n";
                // }
            }
            // if(move==-1){
            //     decklen += 1;
            // }
            
        }

        int getMove(int toDraw, int deckhandlens, int lendeck, int inception){
            // if(inception==0){
            //     vector<int> psbmoves = {0,0,0,0,0,0,0,0,0,0,0,0};
            //     pair<int, int> winpair = simulateGame2(2,hidden,hand,decklen,"theirs",toDraw,)
            // }
            // else{
                int chosenmove = giveRandomMove(hand, name, deckhandlens, numPlayable, lendeck, toDraw);
                if(chosenmove!=0){
                    numPlayable -= 1;
                }
                return chosenmove;
            // }
        }

        int cardDrawn(int card){
            // cout << "Player" << name << " drew " << card << "\n";
            if(card==-1){ //Oh no! An exploding kitten!
                if(hand[0]==0){ // rip ur dead
                    return 0;
                }
                else{ // use a defuse!
                    hand[0] -= 1;
                    numCards -= 1;
                    return 1;
                }
            }
            else{ // safe!
                hand[card] += 1;
                hidden[card] -= 1;
                if(hidden[card] < 0){cout << "Negative! something went wrong lol3 \n";  cout << vectorToString(hidden) << name; cin.get();}
                numCards += 1;
                if(card >= 7){
                    if(hand[card]%2==0){
                        numPlayable += 1;
                    }
                }
                else if(card>=2){
                    numPlayable += 1;
                }
                return 2;
            }
        }

        int getFavored(int toDraw, int deckhandlens, int lendeck){


            int togiveaway = -999;
            
            uint64_t state = toDraw;
            state <<= 4;
            state |= lendeck;

            // const auto &hand = deck;
            for (int i = 0; i < 12; i++) {
                state <<= 3;
                state |= hand[i];
            }

            state <<= 6;
            state |= deckhandlens;


            if(totalstates.find(state)!=totalstates.end()){
                // cout << "HIT\n";
                vector<pair<long,long>> vp = totalstates[state];
                for(int i=0;i<12;i++){
                    if(hand[i]!=0 && vp[i].second==0){
                        int togiveaway = i;
                        break;
                    }
                }
            }
    

            if(togiveaway==-999){
                togiveaway = weightedRandom(hand, numCards);
            }
            hand[togiveaway] -= 1;
            numCards -= 1;
            if(2<=togiveaway && togiveaway<=6){
                numPlayable -= 1;
            }
            else if(togiveaway >= 7 and hand[togiveaway]%2==1){
                numPlayable -= 1;
            }
            return togiveaway;
        }

        int reinsertEK(int decklen){
            return rand()%(decklen+1);
        }

        bool askNope(int toDraw, int move, int deckhandlens){

            bool toNope;
            if(hand[1] > 0){
                toNope = (rand()%2)==0;
            }
            else{
                toNope = false;
            }
            if(toNope){
                hand[1] -= 1;
                numCards -= 1;
                return true;
            }
            else{
                return false;
            }
        }

};


void logtodict(vector<pair<uint64_t,int>>& statestolog, unordered_map<uint64_t, vector<pair<long,long>>>& statedict, int won){


    // I think cpp wants to make me cry
    for(pair<uint64_t,int> p : statestolog){
        auto [it, inserted] = statedict.try_emplace(p.first, 12, pair<long,long>{0,0});
        auto &statevec = it->second;
        if(won == 1){
            statevec[p.second].first  += 1;
        }
        statevec[p.second].second += 1;

    }
}


pair<int,int> simulateGame(int players){
    //starting generator

    vector<int> startingcards = {
        2, 5, 4, 4,
        4, 4, 5,
        4, 4, 4, 4, 4
    };

    vector<int> yours = {
        1,0,0,0,
        0,0,0,0,
        0,0,0,0
    };

    vector<int> deck = {};
    for(int i=1;i<12;i++){
        for(int j=0;j<startingcards[i];j++){
            deck.push_back(i);
        }
    }
    shuffle(deck.begin(),deck.end(),g);
    // vector<int> deck = {1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11};
    
    for(int j=0;j<7;j++){
        yours[deck.back()] += 1;
        startingcards[deck.back()] -= 1;
        deck.pop_back();
    }



    

    return simulateGame2(2,startingcards,yours,35,8,1,0,1,deck);
}


// Assume you are 0, they are 1.

// WARNING: THIS ASSUMES OP CAN HAVE 2+ DEFUSES AT THE START OF TURN 0.
// deckifgiven is nonempty if it is an initial call, empty if it is! (because why would you know what's in the deck?)
pair<int,int> simulateGame2(int players, vector<int> unexposed, vector<int> yours, int lenDeck, int theirs, int toDraw, int turn, int opDefuse, vector<int> deckifgiven){
// int simulateGame(int players){
    
    vector<Player> PLAYERS = {};
    
    vector<int> deck = {};
    if(deckifgiven.size()==0){
        for(int i=1;i<12;i++){
            for(int j=0;j<unexposed[i];j++){
                deck.push_back(i);
            }
        }
        shuffle(deck.begin(),deck.end(),g);
    }
    else{
        deck = deckifgiven;
    }

    int inception = 0;
    if(deckifgiven.size()==0){
        inception += 1;
    }
    // cout << deck.size() << "\n";


    PLAYERS.push_back(Player(0,yours,lenDeck));

    vector<int> ophand = {0,0,0,0,0,0,0,0,0,0,0,0};
    for(int j=0;j<theirs-opDefuse;j++){
        ophand[deck.back()] += 1;
        deck.pop_back();
    }
    for(int j = 0;j<opDefuse;j++){
        ophand[0] += 1;

    }
    

    PLAYERS.push_back(Player(1,ophand,lenDeck));


    
    for(int j=0;j<4-opDefuse-yours[0];j++){
        deck.push_back(0);
    }
    deck.push_back(-1);
    shuffle(deck.begin(),deck.end(),g); 
    int victim = turn^1;

    vector<pair<uint64_t,int>> firststates;
    vector<pair<uint64_t,int>> secondstates;
    vector<pair<uint64_t,int>> firstfavored;
    vector<pair<uint64_t,int>> secondfavored;
    
    
    // cout << "init: " << vectorToString(unexposed) << vectorToString(yours) << vectorToString(PLAYERS[1].hand) << opDefuse+"\n";
    // vector<int> deck = {1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11};
    // shuffle(deck.begin(),deck.end(),g);

    // for(int i=0;i<players;i++){
    //     vector<int> hand = {0,0,0,0,0,0,0,0,0,0,0,0};
    //     for(int j=0;j<7;j++){
    //         hand[deck.back()] += 1;
    //         deck.pop_back();
    //     }
    //     hand[0] += 1; //defuse
    //     PLAYERS.push_back(Player(i,hand));
    // }

    // deck.push_back(0);
    // deck.push_back(0);
    // deck.push_back(-1);
    // shuffle(deck.begin(),deck.end(),g); 
    
    // int turn = 0;
    // int victim = turn^1;
    // int toDraw = 1;
    // vector<pair<uint64_t,int>> firststates;
    // vector<pair<uint64_t,int>> secondstates;
    // vector<pair<uint64_t,int>> firstfavored;
    // vector<pair<uint64_t,int>> secondfavored;
    
    int initmove = -1000;
    while(toDraw>0 && PLAYERS.size()>1){
        int move = 999;
        int simpcards = 999;
        if(deck.size()>=10){
            simpcards = 10;
        }
        else if(deck.size() >= 5){
            simpcards = 5;
        }
        else{
            simpcards = deck.size();
        }


        while(move != 0){
            move = PLAYERS[turn].getMove(toDraw,PLAYERS[victim].numCards, deck.size(), inception);
            if(initmove==-1000){
                initmove = move;
            }
            numberofstates += 1;

            

            // if(deck.size() != PLAYERS[0].decklen){
            //     cout << move << " " << deck.size() << PLAYERS[0].decklen << PLAYERS[1].decklen;
            //     cin.get();
            // }
            // cout << turn << " "<< move << " " << vectorToString(PLAYERS[0].hand) << vectorToString(PLAYERS[1].hand) << victim  << vectorToString(PLAYERS[0].hidden) << vectorToString(PLAYERS[1].hidden) << PLAYERS[0].opDefuse << PLAYERS[1].opDefuse << "\n"; 
            // cin.get();
            if(move!=0){
                PLAYERS[turn].numCards -= 1;
                PLAYERS[turn].hand[move] -= 1;
                if(move>=7){
                    PLAYERS[turn].numCards -= 1;
                    PLAYERS[turn].hand[move] -= 1;    
                }
            }

            // uint64_t state = move;
            // state <<= 4;

            // uint64_t state = toDraw;
            // state <<= 4;
            // state |= simpcards;
            // for(int i=0;i<12;i++){
            //     state <<= 3;
            //     state |= PLAYERS[turn].hand[i];
            // }
            // state <<= 6;
            // state |= PLAYERS[1].hand.size();

            // if(totalstates.find(state)==totalstates.end()){
            //     auto &statevec = totalstates[state];
            //     statevec.reserve(12);
            //     for(int i=0;i<12;i++){
            //         statevec.push_back({0,0});
            //     }
            // }
            // totalstates[state][move].first += 1;
            // totalstates[state][move].second += 1;
            
            uint64_t state = toDraw;
            state <<= 4;
            state |= simpcards;

            const auto &hand = PLAYERS[turn].hand;
            for (int i = 0; i < 12; i++) {
                state <<= 3;
                state |= hand[i];
            }

            state <<= 6;
            state |= PLAYERS[1].hand.size();
            
            if(turn==0){
                firststates.push_back({state,move});
            }
            else if(turn==1){
                secondstates.push_back({state,move});
            }
            else{
                cout << "You a dumdum";
            }
            



            // cout << state<<"\n";

            // cout << "After op" << " " << vectorToString(PLAYERS[0].hand) << vectorToString(PLAYERS[1].hand) << "\n\n"; 
            
            if(move != 4 and move < 7){ // not a favor or a cat card
                PLAYERS[0].inform(turn,move,-999,-999);
                PLAYERS[1].inform(turn,move,-999,-999);
            }
            if(move==0){
                continue;
            }

            bool toNope = PLAYERS[victim].askNope(toDraw,move,PLAYERS[victim].numCards);
            if(toNope){ // not a favor or a cat card
                // cout << "noped\n";
                PLAYERS[0].inform(victim,1,-999,-999);
                PLAYERS[1].inform(victim,1,-999,-999);
                continue;
            }

            if(move==2){
                if(toDraw==1){
                    toDraw += 1;
                }
                else{
                    toDraw += 2;
                }
                turn ^= 1;
                victim = turn^1;
            }
            else if(move==3){
                turn^=1;
                victim = turn^1;
            }
            else if(move==4){
                int favorcard = PLAYERS[victim].getFavored(toDraw, PLAYERS[victim].numCards, deck.size());
                PLAYERS[turn].hand[favorcard] += 1;
                PLAYERS[turn].numCards += 1;
                PLAYERS[0].inform(turn,move,victim,favorcard);
                PLAYERS[1].inform(turn,move,victim,favorcard);
                
                //turn 1 means 0 got favored.
                if(turn==1){
                    firstfavored.push_back({state,favorcard});
                }
                else if(turn==0){
                    secondfavored.push_back({state,favorcard});
                }
                else{
                    cout << "You a dumdum 2\n";
                }

            }
            else if(move==5){
                shuffle(deck.begin(),deck.end(),g);
            }
            else if(move==6){
                //oh look you need to fill this in
            }
            else if(move>=7){
                // cout << 7 << "called by " << turn << "\n";
                int cardtaken = weightedRandom(PLAYERS[victim].hand,PLAYERS[victim].numCards);
                // cout << "Card Taken " << cardtaken<<"\n";
                PLAYERS[victim].hand[cardtaken]-=1;
                PLAYERS[victim].numCards-=1;
                PLAYERS[victim].inform(turn,move,victim,cardtaken);
                PLAYERS[turn].hand[cardtaken]+=1;
                PLAYERS[turn].numCards+=1;
                PLAYERS[turn].inform(turn,move,victim,cardtaken);   
            }
        }
        int nextcard = deck.back();
        deck.pop_back();
        // cout << "Drawn" << nextcard << "\n";
        int safe = PLAYERS[turn].cardDrawn(nextcard);
        if(safe==0){
            PLAYERS.erase(PLAYERS.begin()+turn);
            toDraw = 1;
        }
        else{
            if(safe==1){
                //tell everyone you drew an exploding kitten!
                PLAYERS[0].inform(0,-1,-1000,-1000);
                PLAYERS[1].inform(1,-1,-1000,-1000);
                if(deck.size()==0){
                    deck.push_back(-1);
                }
                else{
                    deck.insert(deck.begin()+(PLAYERS[turn].reinsertEK(deck.size())),-1);
                }
            }
            toDraw -= 1;
            if(toDraw == 0){
                turn ^= 1;
                toDraw = 1;
                victim = turn^1;
            }
        }
    }
    // if(PLAYERS[0].name==0){
    //     logtodict(firststates,totalstates,1);
    //     logtodict(secondstates,totalstates,0);
    //     logtodict(firstfavored,totalfavors,1);
    //     logtodict(secondfavored,totalfavors,0);
    // }
    // else{
    //     logtodict(firststates,totalstates,0);
    //     logtodict(secondstates,totalstates,1); 
    //     logtodict(firstfavored,totalfavors,0);
    //     logtodict(secondfavored,totalfavors,1);   
    // }
    pair<int, int> a = {initmove, PLAYERS[0].name};
    return a;

}


int main(){
    // time_t now = time(0);
    auto start = chrono::high_resolution_clock::now();
    int wins = 0;


    int run = 1'000'00;
    // int run = 1'000'000;

    for(int i=0;i<run;i++){
        pair<int,int> winpair = simulateGame(2);
        if(winpair.second==0){
            wins += 1;
        }
    }

    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
    // cout << time(0)-now << " Seconds\n";
    cout << duration.count()/1'000'000.0 << " seconds\n"; // defaults in microseconds
    //  198290 on 10^5
    //  528909 on 10^6 (2.67x )
    // 1257451 on 10^7 (2.38x )
    cout << "totalstates (no repeats): " << totalstates.size() << "\n";
    //   43933 on 10^5
    //  137236 on 10^6 (3.12x )
    //  367714 on 10^7 (2.68x )
    cout << "totalfavors (no repeats): " << totalfavors.size() << "\n";

    cout << "totalnumberofstates (incl. repeats): " << numberofstates << "\n";
    cout << (wins+0.0)/run << "\n";

}

// With logging

// 1 sec on 10^5 --> 1.10 sec
// 14 sec on 10^6 --> 13.53 sec
// 158 sec on 10^7 --> 154.155 sec


// logless

//  0.573 sec on 10^5
//  5.600 sec on 10^6
// 53.295 sec on 10^7