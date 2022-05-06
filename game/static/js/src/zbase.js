export class AcGame{
    constructor(id, EndOs){
        this.id = id;
        this.$ac_game = $('#' + id);
        this.endos = EndOs;
        this.menu = new AcGameMenu(this);
        this.playground = new AcGamePlayground(this);
        this.settings = new Settings(this);
        this.start();
    }
    start(){
    }
}
