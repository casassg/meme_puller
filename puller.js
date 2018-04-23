const NineGag = require('9gag');
const Scraper = NineGag.Scraper;
const Downloader = NineGag.Downloader;
const fs = require('fs');

const scraper = new Scraper(5000, 'hot', 0);
scraper.scrap()
    .then(posts => {
        let newposts = posts.filter(function(post) {
            return (post.type === 'Image');
        })
        console.log('Scrapping done, downloading');
        const content = JSON.stringify(newposts);

        fs.writeFile("memes.json", content, 'utf8', function (err) {
            if (err) {
                return console.log(err);
            }
        console.log("The file was saved!");
    });
        //return new Downloader('output').downloadPosts(newposts);

    })
    .then(() => {
        console.log('Finished writing html page.');
    })
    .catch(err => console.error(err));
