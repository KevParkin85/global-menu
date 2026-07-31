-- Create the tables
CREATE TABLE national_dishes (
    iso_code VARCHAR(3) PRIMARY KEY,
    dish_name VARCHAR(100),
    method TEXT,
    wiki_url VARCHAR(255)
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    iso_code VARCHAR(3) REFERENCES national_dishes(iso_code),
    ingredient_name VARCHAR(50)
);

-- Insert initial seed dishes
INSERT INTO national_dishes (iso_code, dish_name, method, wiki_url) VALUES 
('ITA', 'Pizza Margherita', 'Prepare the dough using flour, water, and yeast. Leave to prove. Stretch into a base, top with crushed tomatoes and mozzarella cheese, and bake at the highest heat possible. Garnish with fresh basil.', 'https://en.wikipedia.org/wiki/Pizza_Margherita'),
('JPN', 'Shoyu Ramen', 'Boil the noodles. Heat the broth and mix with soy sauce. Combine in a bowl and top with sliced roast pork, a soft-boiled egg, and freshly chopped scallions.', 'https://en.wikipedia.org/wiki/Ramen'),
('FRA', 'French Onion Soup', 'Slowly caramelize the onions in butter until deeply browned. Add the beef broth and simmer. Ladle into bowls, top with toasted bread and grated cheese, then melt under a grill.', 'https://en.wikipedia.org/wiki/French_onion_soup'),
('GBR', 'Fish and Chips', 'Cut the potatoes into chips and fry until golden. Create a batter with flour and water, coat the fish, and deep fry until crisp. Serve hot with salt and vinegar.', 'https://en.wikipedia.org/wiki/Fish_and_chips');

-- Insert initial seed ingredients
INSERT INTO ingredients (iso_code, ingredient_name) VALUES 
('ITA', 'flour'), ('ITA', 'water'), ('ITA', 'yeast'), ('ITA', 'tomatoes'), ('ITA', 'cheese'), ('ITA', 'basil'),
('JPN', 'noodles'), ('JPN', 'soy sauce'), ('JPN', 'pork'), ('JPN', 'egg'), ('JPN', 'scallions'), ('JPN', 'broth'),
('FRA', 'onions'), ('FRA', 'beef broth'), ('FRA', 'bread'), ('FRA', 'cheese'), ('FRA', 'butter'),
('GBR', 'fish'), ('GBR', 'potatoes'), ('GBR', 'flour'), ('GBR', 'oil'), ('GBR', 'salt'), ('GBR', 'vinegar');