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

using namespace std;

mt19937 g(12);


int hit = 0;
int cache = 0;
unordered_map<string,unordered_map<int,int>> totalstates;



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
    if(total == 0){
        return 0;
    }

    // cout << vectorToString(possible) << " " << vectorToString(deck) << "\n";
    return weightedRandom(possible,total);
    // }


}




class Player{
    public:
        int name;
        int numPlayable;
        int numCards;
        vector<int> hand;

        Player(int n, vector<int> h){
            name = n;
            hand = h;
            numCards = 8;
            numPlayable = hand[2]+hand[3]+hand[4]+hand[5]+hand[6]+hand[7]/2+hand[8]/2+hand[9]/2+hand[10]/2+hand[11]/2;
        }
    
        void inform(int player, int move, int victim, int cardtaken){
            if(player!=name && move>=7 && victim==name){
                if(cardtaken>=2 && cardtaken<=6){
                    numPlayable-=1;
                }
                else if(cardtaken >= 7 and hand[cardtaken]%2==1){
                    numPlayable-=1;
                }
            }
            else if(player==name && (move==4 || move>=7)){
                if(cardtaken>=2 && cardtaken<=6){
                    numPlayable+=1;
                }
                else if(cardtaken >= 7 and hand[cardtaken]%2==0){
                    numPlayable+=1;
                }
            }
        }

        int getMove(int toDraw, int deckhandlens, int lendeck){
            int chosenmove = giveRandomMove(hand, name, deckhandlens, numPlayable, lendeck, toDraw);
            if(chosenmove!=0){
                numPlayable -= 1;
            }
            return chosenmove;
        }

        int cardDrawn(int card){
            if(card==-1){
                if(hand[0]==0){
                    return 0;
                }
                else{
                    hand[0] -= 1;
                    numCards -= 1;
                    return 1;
                }
            }
            else{
                hand[card] += 1;
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

        int getFavored(){
            int togiveaway = weightedRandom(hand, numCards);
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





int simulateGame(int players){
    vector<int> deck = {1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11};
    vector<Player> PLAYERS = {};
    shuffle(deck.begin(),deck.end(),g);

    for(int i=0;i<players;i++){
        vector<int> hand = {0,0,0,0,0,0,0,0,0,0,0,0};
        for(int j=0;j<7;j++){
            hand[deck.back()] += 1;
            deck.pop_back();
        }
        hand[0] += 1; //defuse
        PLAYERS.push_back(Player(i,hand));
    }

    deck.push_back(0);
    deck.push_back(0);
    deck.push_back(-1);
    shuffle(deck.begin(),deck.end(),g); 
    
    int turn = 0;
    int victim = 1;
    int toDraw = 1;

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
            move = PLAYERS[turn].getMove(toDraw,PLAYERS[victim].numCards, simpcards);

            // cout << turn << " "<< move << " " << vectorToString(PLAYERS[0].hand) << vectorToString(PLAYERS[1].hand) << victim << "\n"; 

            if(move!=0){
                PLAYERS[turn].numCards -= 1;
                PLAYERS[turn].hand[move] -= 1;
                if(move>=7){
                    PLAYERS[turn].numCards -= 1;
                    PLAYERS[turn].hand[move] -= 1;    
                }
            }
            // cout << "After op" << " " << vectorToString(PLAYERS[0].hand) << vectorToString(PLAYERS[1].hand) << "\n\n"; 
            
            if(move==0){
                continue;
            }

            bool toNope = PLAYERS[victim].askNope(toDraw,move,PLAYERS[victim].numCards);
            if(toNope){continue;}

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
                int favorcard = PLAYERS[victim].getFavored();
                PLAYERS[turn].hand[favorcard] += 1;
                PLAYERS[turn].numCards += 1;
                PLAYERS[turn].inform(turn,move,victim,favorcard);
            }
            else if(move==5){
                shuffle(deck.begin(),deck.end(),g);
            }
            else if(move==6){
                //oh look you need to fill this in
            }
            else if(move>=7){
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
    return PLAYERS[0].name;

}


int main(){
    time_t now = time(0);
    for(int i=0;i<1000000;i++){
        simulateGame(2);
    }
    cout << time(0)-now << " Seconds\n";
}